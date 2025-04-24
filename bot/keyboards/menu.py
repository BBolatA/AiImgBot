from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, WebAppInfo
from ..config import settings


def main_menu(user_id: int) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()

    kb.button(text="🖼  Сгенерировать картинку")
    kb.button(
        text="🎞  Галерея",
        web_app=WebAppInfo(url=f"{settings.base_url}/gallery/?uid={user_id}")
    )
    kb.button(text="ℹ️  Помощь")
    kb.button(text="⚙️  Настройки")

    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)