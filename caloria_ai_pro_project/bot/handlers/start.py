from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from core.db import get_or_create_user
from bot.keyboards import main_menu_kb

router = Router()

# Для продакшена сюда можно положить URL из env/конфига
DASHBOARD_BASE_URL = "https://your-caloria-pro-domain"


@router.message(CommandStart())
async def cmd_start(message: Message):
    await get_or_create_user(
        telegram_id=message.from_user.id,
        name=message.from_user.full_name,
    )

    kb = main_menu_kb(
        telegram_id=message.from_user.id,
        dashboard_base_url=DASHBOARD_BASE_URL,
    )

    await message.answer(
        "👋 Привет! Я <b>Caloria AI Pro</b>.

"
        "Отправь мне, что ты съел — я проанализирую приём пищи и сохраню его в твой дневник.
"
        "Статистику за день можно посмотреть в веб-дэшборде.",
        reply_markup=kb,
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    kb = main_menu_kb(
        telegram_id=message.from_user.id,
        dashboard_base_url=DASHBOARD_BASE_URL,
    )
    await message.answer("Главное меню:", reply_markup=kb)


@router.callback_query(lambda c: c.data == "add_meal")
async def cb_add_meal(callback: CallbackQuery):
    await callback.message.answer(
        "✍ Напиши одним сообщением, что ты сейчас съел.

"
        "Например: <i>“овсянка на молоке и банан”</i>"
    )
    await callback.answer()
