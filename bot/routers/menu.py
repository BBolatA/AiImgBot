from aiogram.filters import Command
from aiogram import Router, types, F
from aiogram.types import Message

from ..keyboards.menu import main_menu

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    text = (
        "👋 Привет! Я AI-генератор изображений.\n\n"
        "Выберите действие:"
    )
    await message.answer(text, reply_markup=main_menu(message.chat.id))


@router.message(F.text == "🖼  Сгенерировать картинку")
async def shortcut_img(message: Message):
    await message.answer(
        "Отправьте команду в формате:\n"
        "<code>/img ваш_промпт</code>"
    )


@router.message(F.text == "ℹ️  Помощь")
async def shortcut_help(message: Message):
    await message.answer(
        "Доступные команды:\n"
        "• <code>/img ваш_промпт</code> — сгенерировать изображение\n"
        "• <code>⚙️ Настройки</code> — поменять опции\n"
        "• <code>/start</code> — в начало"
    )
