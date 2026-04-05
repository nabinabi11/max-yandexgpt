"""Custom bot — with system prompt, non-streaming, and env variables."""

import os

from max_yandexgpt import MaxYandexGPT

bot = MaxYandexGPT(
    max_token=os.getenv("MAX_TOKEN"),
    yandex_api_key=os.getenv("YANDEX_API_KEY"),
    yandex_folder_id=os.getenv("YANDEX_FOLDER_ID"),
    system_prompt="Ты — дружелюбный помощник. Отвечай кратко и по делу.",
    stream=False,       # Без стриминга — один ответ целиком
    temperature=0.5,
    max_tokens=1000,
)
bot.run()
