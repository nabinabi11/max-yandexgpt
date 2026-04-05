"""Configuration for max-yandexgpt."""

from dataclasses import dataclass

MODELS = {
    "yandexgpt-5.1": "yandexgpt-5.1/latest",
    "yandexgpt-5-pro": "yandexgpt-5-pro/latest",
    "yandexgpt-5-lite": "yandexgpt-5-lite/latest",
    "aliceai": "aliceai-llm/latest",
}

DEFAULT_MODEL = "yandexgpt-5-lite/latest"


@dataclass
class Config:
    """Bot configuration.

    Args:
        max_token: Max messenger bot token.
        yandex_api_key: YandexGPT API key.
        yandex_folder_id: Yandex Cloud folder ID.
        model: YandexGPT model name (e.g. 'yandexgpt-5-lite/latest').
        system_prompt: System prompt for the LLM.
        temperature: Generation temperature (0.0 - 1.0).
        max_tokens: Maximum tokens in LLM response.
        stream: Enable streaming responses with message editing.
        stream_interval: Seconds between message edits during streaming.
    """

    max_token: str = ""
    yandex_api_key: str = ""
    yandex_folder_id: str = ""
    model: str = DEFAULT_MODEL
    system_prompt: str = "Ты — полезный ассистент."
    temperature: float = 0.3
    max_tokens: int = 2000
    stream: bool = True
    stream_interval: float = 1.0

    def validate(self):
        """Validate that required fields are set."""
        if not self.max_token:
            raise ValueError("max_token is required")
        if not self.yandex_api_key:
            raise ValueError("yandex_api_key is required")
        if not self.yandex_folder_id:
            raise ValueError("yandex_folder_id is required")
