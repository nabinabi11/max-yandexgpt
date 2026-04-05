"""YandexGPT client with sync and streaming support."""

import json
from collections.abc import AsyncIterator
from dataclasses import dataclass

import aiohttp

from .config import Config

YANDEXGPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"


@dataclass
class LLMResponse:
    """Response from YandexGPT."""

    text: str
    tokens_input: int = 0
    tokens_output: int = 0


class YandexGPT:
    """YandexGPT API client."""

    def __init__(self, config: Config):
        self.config = config
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Api-Key {self.config.yandex_api_key}",
                    "x-folder-id": self.config.yandex_folder_id,
                    "Content-Type": "application/json",
                }
            )
        return self._session

    def _build_payload(self, messages: list[dict], stream: bool = False) -> dict:
        return {
            "modelUri": self.config.model,
            "completionOptions": {
                "stream": stream,
                "temperature": self.config.temperature,
                "maxTokens": str(self.config.max_tokens),
            },
            "messages": messages,
        }

    def _build_messages(self, user_text: str, history: list[dict] | None = None) -> list[dict]:
        messages = [{"role": "system", "text": self.config.system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "text": user_text})
        return messages

    async def complete(
        self, user_text: str, history: list[dict] | None = None
    ) -> LLMResponse:
        """Send a non-streaming completion request."""
        messages = self._build_messages(user_text, history)
        payload = self._build_payload(messages, stream=False)

        session = await self._get_session()
        async with session.post(YANDEXGPT_URL, json=payload) as resp:
            resp.raise_for_status()
            data = await resp.json()

        alt = data["result"]["alternatives"][0]
        usage = data["result"].get("usage", {})
        return LLMResponse(
            text=alt["message"]["text"],
            tokens_input=int(usage.get("inputTextTokens", 0)),
            tokens_output=int(usage.get("completionTokens", 0)),
        )

    async def stream(
        self, user_text: str, history: list[dict] | None = None
    ) -> AsyncIterator[str]:
        """Send a streaming completion request. Yields accumulated text chunks."""
        messages = self._build_messages(user_text, history)
        payload = self._build_payload(messages, stream=True)

        session = await self._get_session()
        prev_len = 0

        async with session.post(YANDEXGPT_URL, json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.content:
                decoded = line.decode("utf-8").strip()
                if not decoded:
                    continue

                try:
                    data = json.loads(decoded)
                except json.JSONDecodeError:
                    continue

                alt = data.get("result", {}).get("alternatives", [{}])[0]
                full_text = alt.get("message", {}).get("text", "")

                # YandexGPT streaming returns accumulated text, extract delta
                if len(full_text) > prev_len:
                    delta = full_text[prev_len:]
                    prev_len = len(full_text)
                    yield delta

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
