from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


def _builder_from_choices(prefix: str, choices, per_row: int = 3) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for text, val in choices:
        b.button(text=text, callback_data=f"{prefix}:{val}")
    b.adjust(per_row)
    return b.as_markup()


def format_kb() -> InlineKeyboardMarkup:
    choices = [("PNG", "png"), ("JPEG", "jpeg"), ("WEBP", "webp")]
    return _builder_from_choices("set_fmt", choices, per_row=3)


def main_settings_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="Формат", callback_data="chg_fmt")
    b.adjust(1)
    return b.as_markup()
