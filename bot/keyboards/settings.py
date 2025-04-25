from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


def resolution_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    choices = [
        ("1152×896", "1152*896"),
        ("1280×768", "1280*768"),
        ("1024×1024", "1024*1024"),
        ("768×1280", "768*1280"),
        ("896×1152", "896*1152"),
    ]
    for text, val in choices:
        builder.button(text=text, callback_data=f"set_res:{val}")
    builder.adjust(2)
    return builder.as_markup()


def quality_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    choices = [("Quality", "Quality"), ("Speed", "Speed"), ("Extreme Speed", "Extreme Speed")]
    for text, val in choices:
        builder.button(text=text, callback_data=f"set_q:{val}")
    builder.adjust(3)
    return builder.as_markup()


def format_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    choices = [("PNG", "png"), ("JPEG", "jpeg"), ("WEBP", "webp")]
    for text, val in choices:
        builder.button(text=text, callback_data=f"set_fmt:{val}")
    builder.adjust(3)
    return builder.as_markup()
