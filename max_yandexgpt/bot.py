"""Main bot class — ties Max messenger with YandexGPT."""

import asyncio
import logging
import os

from maxapi import Bot, Dispatcher
from maxapi.types import BotStartedUpdate, MessageCreatedUpdate
from maxapi.filters import F

from .config import Config
from .llm import YandexGPT

logger = logging.getLogger("max_yandexgpt")


class MaxYandexGPT:
    """Max messenger bot powered by YandexGPT.

    Minimal usage::

        from max_yandexgpt import MaxYandexGPT

        bot = MaxYandexGPT(
            max_token="...",
            yandex_api_key="...",
            yandex_folder_id="...",
        )
        bot.run()
    """

    def __init__(
        self,
        max_token: str | None = None,
        yandex_api_key: str | None = None,
        yandex_folder_id: str | None = None,
        *,
        config: Config | None = None,
        system_prompt: str | None = None,
        stream: bool | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ):
        if config:
            self.config = config
        else:
            self.config = Config(
                max_token=max_token or os.getenv("MAX_TOKEN", ""),
                yandex_api_key=yandex_api_key or os.getenv("YANDEX_API_KEY", ""),
                yandex_folder_id=yandex_folder_id or os.getenv("YANDEX_FOLDER_ID", ""),
            )

        if system_prompt is not None:
            self.config.system_prompt = system_prompt
        if stream is not None:
            self.config.stream = stream
        if temperature is not None:
            self.config.temperature = temperature
        if max_tokens is not None:
            self.config.max_tokens = max_tokens

        self.config.validate()

        self.bot = Bot(token=self.config.max_token)
        self.dp = Dispatcher(self.bot)
        self.llm = YandexGPT(self.config)

        self._register_handlers()

    def _register_handlers(self):
        """Register default message handlers."""

        @self.dp.bot_started()
        async def on_start(event: BotStartedUpdate):
            await event.message.answer("Привет! Я бот с YandexGPT. Напиши мне что-нибудь.")

        @self.dp.message_created(F.message.body.text)
        async def on_message(event: MessageCreatedUpdate):
            user_text = event.message.body.text

            if self.config.stream:
                await self._handle_streaming(event, user_text)
            else:
                await self._handle_sync(event, user_text)

    async def _handle_sync(self, event: MessageCreatedUpdate, user_text: str):
        """Handle message with non-streaming YandexGPT response."""
        try:
            response = await self.llm.complete(user_text)
            await event.message.answer(response.text)
        except Exception as e:
            logger.error("YandexGPT error: %s", e)
            await event.message.answer("Произошла ошибка при обращении к YandexGPT.")

    async def _handle_streaming(self, event: MessageCreatedUpdate, user_text: str):
        """Handle message with streaming YandexGPT response + message editing."""
        try:
            # Send placeholder
            sent = await event.message.answer("...")
            message_id = sent.message.body.mid
            accumulated = ""
            last_edit = 0.0

            async for delta in self.llm.stream(user_text):
                accumulated += delta
                now = asyncio.get_event_loop().time()

                # Rate-limit edits
                if now - last_edit >= self.config.stream_interval:
                    await self.bot.edit_message(message_id=message_id, text=accumulated + " ...")
                    last_edit = now

            # Final edit with complete text
            if accumulated:
                await self.bot.edit_message(message_id=message_id, text=accumulated)

        except Exception as e:
            logger.error("Streaming error: %s", e)
            await event.message.answer("Произошла ошибка при обращении к YandexGPT.")

    def run(self):
        """Start the bot (blocking)."""
        logger.info("Starting MaxYandexGPT bot...")
        try:
            asyncio.run(self._run_polling())
        except KeyboardInterrupt:
            logger.info("Bot stopped.")

    async def _run_polling(self):
        """Internal async entry point."""
        try:
            await self.dp.start_polling()
        finally:
            await self.llm.close()
