from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)
class Settings:
    bot_token: str
    openai_api_key: str | None
    database_path: str


def get_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "")
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is not set in environment or .env file")

    openai_key = os.getenv("OPENAI_API_KEY") or None
    db_path = os.getenv("DATABASE_PATH", "caloria_pro.db")

    return Settings(
        bot_token=bot_token,
        openai_api_key=openai_key,
        database_path=db_path,
    )


settings = get_settings()
