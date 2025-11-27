from aiogram import Router, F
from aiogram.types import Message

from core.ai_meals import analyze_meal_text
from core.db import get_or_create_user, add_meal

router = Router()


@router.message(F.text & ~F.text.startswith("/"))
async def handle_meal_text(message: Message):
    """Любой не-командный текст считаем описанием еды."""
    user_id = await get_or_create_user(
        telegram_id=message.from_user.id,
        name=message.from_user.full_name,
    )

    user_text = message.text.strip()
    if not user_text:
        await message.answer("Сообщение пустое, опиши, пожалуйста, приём пищи текстом.")
        return

    analysis = analyze_meal_text(user_text)
    calories = float(analysis.get("calories", 350))

    await add_meal(
        user_id=user_id,
        description=analysis.get("description", user_text),
        calories=calories,
    )

    await message.answer(
        "✅ Я записал твой приём пищи.

"
        f"📝 <b>Описание:</b> {analysis['description']}
"
        f"🔥 <b>Калории (примерно):</b> {int(calories)} ккал
"
        f"💭 <b>Комментарий:</b> {analysis['goal_hint']}
"
        f"🤖 Источник анализа: <code>{analysis['source']}</code>

"
        "Можешь отправить следующий приём или открыть дашборд для обзора дня."
    )
