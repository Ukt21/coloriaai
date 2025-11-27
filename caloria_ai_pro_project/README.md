# Caloria AI Pro — Telegram-бот + веб-дэшборд с ИИ-анализом питания

Проект уровня продакшена с разделением на слои:

- `bot/` — Telegram-бот на `aiogram 3`
- `core/` — база данных и ИИ-логика
- `web/` — веб-дэшборд на `FastAPI`
- `config.py` — конфигурация через `.env`

## 1. Установка

```bash
pip install -r requirements.txt
cp .env.example .env
```

В `.env` задайте:

- `BOT_TOKEN` — токен вашего Telegram-бота
- `OPENAI_API_KEY` — (опционально) ключ OpenAI, если хотите анализ еды через ИИ
- `DATABASE_PATH` — путь до SQLite-файла (по умолчанию `caloria_pro.db`)

## 2. Запуск бота локально

```bash
python -m bot.main
```

Бот:

- регистрирует пользователя по `/start`
- любому тексту (кроме команд `/...`) считает, что это описание приёма пищи
- анализирует приём (через OpenAI или эвристику)
- сохраняет приём в БД
- отвечает оценкой калорий и комментариями

## 3. Запуск веб-дэшборда локально

```bash
uvicorn web.main:app --reload
```

- Главная: `http://127.0.0.1:8000/`
- Дэшборд пользователя: `http://127.0.0.1:8000/dashboard/<telegram_id>`

`<telegram_id>` — это `message.from_user.id`.  
Бот даёт кнопку «Открыть дашборд» с уже подставленным ID, когда вы пропишете реальный домен.

## 4. Настройка доменов и ссылок

- В `bot/handlers/start.py` замените:

```python
DASHBOARD_BASE_URL = "https://your-caloria-pro-domain"
```

на ваш реальный URL, например:

```python
DASHBOARD_BASE_URL = "https://caloria-pro.onrender.com"
```

- В `web/templates/index.html` замените ссылку:

```html
href="https://t.me/your_caloria_pro_bot"
```

на реального бота.

## 5. Деплой на Render

В проекте есть `render.yaml` с двумя сервисами:

- `caloria-pro-web` — FastAPI-приложение
- `caloria-pro-bot` — Telegram-бот (worker)

Шаги:

1. Загрузите проект в GitHub.
2. На Render создайте Blueprint (New → Blueprint) и укажите репозиторий.
3. Задайте переменные окружения:
   - `BOT_TOKEN`
   - `OPENAI_API_KEY` (опционально)
   - `DATABASE_PATH` (можно оставить по умолчанию)
4. Нажмите Deploy.

После деплоя бот и веб-дэшборд будут работать совместно.

Проект можно расширять:

- добавить поддержку голосовых и фото,
- подключить настоящие данные активности,
- сделать историю за неделю/месяц,
- реализовать подписки и тарифы.
