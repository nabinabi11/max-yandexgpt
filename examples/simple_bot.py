"""Minimal bot example — 5 lines to a working YandexGPT bot in Max."""

from max_yandexgpt import MaxYandexGPT

bot = MaxYandexGPT(
    max_token="YOUR_MAX_TOKEN",
    yandex_api_key="YOUR_YANDEX_API_KEY",
    yandex_folder_id="YOUR_FOLDER_ID",
)
bot.run()
