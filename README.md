# max-yandexgpt

Python-фреймворк для создания ботов в Max мессенджере с YandexGPT.

5 строк кода — и у вас работающий AI-бот со стримингом ответов.

## Быстрый старт

```bash
pip install max-yandexgpt
```

```python
from max_yandexgpt import MaxYandexGPT

bot = MaxYandexGPT(
    max_token="ВАШ_ТОКЕН_MAX",
    yandex_api_key="ВАШ_КЛЮЧ_YANDEXGPT",
    yandex_folder_id="ВАШ_FOLDER_ID",
)
bot.run()
```

## Возможности

- **Стриминг ответов** — бот отправляет placeholder, затем обновляет сообщение по мере генерации текста YandexGPT
- **Обычный режим** — простой запрос-ответ, одно сообщение
- **Выбор модели** — поддержка всех моделей YandexGPT
- **Настройка** — system prompt, температура, max_tokens
- **Переменные окружения** — задайте `MAX_TOKEN`, `YANDEX_API_KEY`, `YANDEX_FOLDER_ID` вместо хардкода

## Модели

| Модель | Описание |
|--------|----------|
| `yandexgpt-5-lite/latest` | Быстрая и дешёвая (по умолчанию) |
| `yandexgpt-5-pro/latest` | Стандартная |
| `yandexgpt-5.1/latest` | Новейшая |
| `aliceai-llm/latest` | AliceAI |

```python
bot = MaxYandexGPT(
    max_token="...",
    yandex_api_key="...",
    yandex_folder_id="...",
    model="yandexgpt-5.1/latest",
)
```

## Настройка

```python
bot = MaxYandexGPT(
    max_token="...",
    yandex_api_key="...",
    yandex_folder_id="...",
    system_prompt="Ты — полезный ассистент.",
    stream=True,           # стриминг включён по умолчанию
    temperature=0.3,
    max_tokens=2000,
)
```

Или через переменные окружения:

```python
bot = MaxYandexGPT()  # читает из MAX_TOKEN, YANDEX_API_KEY, YANDEX_FOLDER_ID
bot.run()
```

## Требования

- Python 3.11+
- Токен бота Max мессенджера ([создать бота](https://max.ru))
- API-ключ YandexGPT + folder ID ([Yandex Cloud](https://cloud.yandex.ru))

## Лицензия

MIT
