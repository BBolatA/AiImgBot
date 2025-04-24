from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types


def qty_keyboard(prompt: str) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for qty, label in [(1, "➊ 1 фото"), (2, "➋ 2 фото"), (4, "➍ 4 фото")]:
        kb.button(text=label, callback_data=f"gen:{qty}:{prompt}")
    kb.adjust(1)
    kb.button(text="✖ Отмена", callback_data="cancel")
    return kb.as_markup()


def post_action_keyboard(prompt: str) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="↺ Retry",  callback_data=f"retry:{prompt}")
    kb.button(text="🗑 Delete", callback_data="delete")
    kb.adjust(2)
    return kb.as_markup()
