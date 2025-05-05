from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from ..keyboards.menu import main_menu

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я AI-генератор изображений.\n\nВыберите действие:",
        reply_markup=main_menu()
    )


@router.callback_query(F.data == "gen:start")
async def cb_gen_start(call: CallbackQuery):
    await call.message.answer(
        "Отправьте команду в формате:\n<code>/img ваш_промпт</code>"
    )
    await call.answer()

HELP_TEXT = (
    "Доступные команды:\n"
    "• <code>/img ваш_промпт</code> — сгенерировать изображение\n"
    "• ⚙️ Настройки — поменять опции\n"
    "• <code>/start</code> — в начало"
)


@router.callback_query(F.data == "help:show")
async def cb_help(call: CallbackQuery):
    await call.message.answer(HELP_TEXT, parse_mode="HTML")
    await call.answer()
