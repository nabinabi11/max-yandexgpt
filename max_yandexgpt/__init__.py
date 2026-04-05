"""max-yandexgpt — Max messenger + YandexGPT integration framework."""

from .bot import MaxYandexGPT
from .config import Config
from .llm import LLMResponse, YandexGPT

__version__ = "0.1.0"
__all__ = ["MaxYandexGPT", "Config", "YandexGPT", "LLMResponse"]
