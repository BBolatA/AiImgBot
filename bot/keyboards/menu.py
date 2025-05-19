from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from ..config import settings


def main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text="🖼  Сгенерировать картинку", callback_data="gen:start")
    kb.button(
        text="🎞  Галерея",
        web_app=WebAppInfo(url=f"{settings.base_url}/gallery/")
    )
    kb.button(text="ℹ️  Помощь",    callback_data="help:show")
    kb.button(text="⚙️  Настройки", callback_data="settings:open")

    kb.adjust(1)
    return kb.as_markup()
