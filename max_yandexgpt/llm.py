"""YandexGPT client via OpenAI-compatible API."""

from collections.abc import AsyncIterator
from dataclasses import dataclass

from openai import AsyncOpenAI

from .config import Config

YANDEX_BASE_URL = "https://ai.api.cloud.yandex.net/v1"


@dataclass
class LLMResponse:
    """Response from YandexGPT."""

    text: str
    tokens_input: int = 0
    tokens_output: int = 0


class YandexGPT:
    """YandexGPT API client (OpenAI-compatible)."""

    def __init__(self, config: Config):
        self.config = config
        self._client = AsyncOpenAI(
            api_key=config.yandex_api_key,
            base_url=YANDEX_BASE_URL,
        )

    def _model_uri(self) -> str:
        return f"gpt://{self.config.yandex_folder_id}/{self.config.model}"

    def _build_messages(self, user_text: str, history: list[dict] | None = None) -> list[dict]:
        messages = [{"role": "system", "content": self.config.system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_text})
        return messages

    async def complete(
        self, user_text: str, history: list[dict] | None = None
    ) -> LLMResponse:
        """Send a non-streaming completion request."""
        messages = self._build_messages(user_text, history)

        response = await self._client.chat.completions.create(
            model=self._model_uri(),
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=False,
            extra_headers={"x-folder-id": self.config.yandex_folder_id},
        )

        choice = response.choices[0]
        usage = response.usage
        return LLMResponse(
            text=choice.message.content or "",
            tokens_input=usage.prompt_tokens if usage else 0,
            tokens_output=usage.completion_tokens if usage else 0,
        )

    async def stream(
        self, user_text: str, history: list[dict] | None = None
    ) -> AsyncIterator[str]:
        """Send a streaming completion request. Yields text deltas."""
        messages = self._build_messages(user_text, history)

        response = await self._client.chat.completions.create(
            model=self._model_uri(),
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=True,
            extra_headers={"x-folder-id": self.config.yandex_folder_id},
        )

        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def close(self):
        """Close the HTTP client."""
        await self._client.close()
