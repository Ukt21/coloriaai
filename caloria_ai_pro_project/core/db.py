from __future__ import annotations

from typing import Optional, Dict, List, Tuple

import aiosqlite

from config import settings

DB_PATH = settings.database_path


async def init_db() -> None:
    """Создаёт таблицы, если их ещё нет."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                name TEXT
            );
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                calories REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """)

        await db.commit()


async def get_or_create_user(telegram_id: int, name: Optional[str] = None) -> int:
    """Возвращает внутренний ID пользователя, создаёт при необходимости."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            "SELECT id FROM users WHERE telegram_id = ?",
            (telegram_id,),
        )
        row = await cur.fetchone()
        await cur.close()

        if row:
            return row["id"]

        cur = await db.execute(
            "INSERT INTO users (telegram_id, name) VALUES (?, ?)",
            (telegram_id, name),
        )
        await db.commit()
        return cur.lastrowid


async def add_meal(user_id: int, description: str, calories: float) -> None:
    """Сохраняет приём пищи."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO meals (user_id, description, calories) VALUES (?, ?, ?)",
            (user_id, description, calories),
        )
        await db.commit()


async def get_today_stats(user_id: int) -> Dict:
    """Возвращает статистику за сегодня для пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """
            SELECT 
                COUNT(*) AS meals_count,
                COALESCE(SUM(calories), 0) AS total_calories
            FROM meals
            WHERE user_id = ?
              AND DATE(created_at) = DATE('now', 'localtime')
            """,
            (user_id,),
        )
        row = await cur.fetchone()
        await cur.close()

        return {
            "meals_count": int(row["meals_count"]),
            "total_calories": float(row["total_calories"]),
        }


async def get_recent_meals(user_id: int, limit: int = 5) -> List[Dict]:
    """Последние N приёмов пищи."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """
            SELECT description, calories, created_at
            FROM meals
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        rows = await cur.fetchall()
        await cur.close()

        return [
            {
                "description": r["description"],
                "calories": float(r["calories"]),
                "created_at": r["created_at"],
            }
            for r in rows
        ]


async def get_rings_for_user(telegram_id: int) -> Tuple[float, float, float]:
    """Возвращает значения прогресса колец (0..1).

    На основе общей суммы калорий и количества приёмов пищи.
    """
    user_id = await get_or_create_user(telegram_id=telegram_id)

    stats = await get_today_stats(user_id)
    total_calories = stats["total_calories"]
    meals_count = stats["meals_count"]

    calories_ring = min(total_calories / 2000.0, 1.0) if total_calories > 0 else 0.0
    protein_ring = min(meals_count / 4.0, 1.0) if meals_count > 0 else 0.0
    activity_ring = 0.4  # Заглушка, можно привязать к шагам/активности

    return calories_ring, protein_ring, activity_ring
