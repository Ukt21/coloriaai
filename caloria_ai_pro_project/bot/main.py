import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config import settings
from core.db import init_db
from bot.handlers import start_router, meals_router
from bot.logging_config import setup_logging


async def main() -> None:
    setup_logging()
    logging.info("Starting Caloria AI Pro bot...")

    await init_db()
    logging.info("Database initialized")

    bot = Bot(token=settings.bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(meals_router)

    logging.info("Bot is polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
