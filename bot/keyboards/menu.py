from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, WebAppInfo
from django.conf import settings


def main_menu(user_id: int) -> ReplyKeyboardMarkup:
    """
    Возвращает ReplyKeyboardMarkup, где кнопка «Галерея» открывает WebApp
    с ?uid=<user_id> в конце.
    """
    kb = ReplyKeyboardBuilder()

    kb.button(text="🖼  Сгенерировать картинку")
    kb.button(
        text="🎞  Галерея",
        web_app=WebAppInfo(url=f"{settings.BASE_URL}/gallery/?uid={user_id}")
    )
    kb.button(text="ℹ️  Помощь")
    kb.button(text="⚙️  Настройки")

    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)