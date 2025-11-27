from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_kb(telegram_id: int, dashboard_base_url: str) -> InlineKeyboardMarkup:
    """Основное меню бота.

    dashboard_base_url ожидается без завершающего слеша,
    например: https://caloria.onrender.com
    """
    dashboard_url = f"{dashboard_base_url}/dashboard/{telegram_id}"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Записать приём пищи",
                    callback_data="add_meal",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Открыть дашборд",
                    url=dashboard_url,
                )
            ],
        ]
    )
