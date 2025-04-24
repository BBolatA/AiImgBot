from aiogram import Router, types, F
from aiogram.filters import Command
from ..keyboards.menu import main_menu

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    text = (
        "👋 Привет! Я AI‑генератор изображений.\n\n"
        "Выберите действие:"
    )
    await message.answer(text, reply_markup=main_menu(message.chat.id))


@router.message(F.text == "🖼  Сгенерировать картинку")
async def shortcut_img(message: types.Message):
    await message.answer(
        "Отправьте команду в формате:\n"
        "<code>/img A close-up of a witch with intense, glowing eyes, her face partially shadowed, adorned with intricate silver jewelry and floral patterns painted on her skin, surrounded by swirling mist.</code>"
    )


@router.message(F.text == "ℹ️  Помощь")
async def shortcut_help(message: types.Message):
    await message.answer(
        "Доступные команды:\n"
        "• <code>/img ваш_промпт</code> — сгенерировать изображение\n"
        "• <code>/settings</code> — настройки (скоро)\n"
        "• <code>/help</code> — эта справка"
    )


@router.message(F.text == "⚙️  Настройки")
async def shortcut_settings(message: types.Message):
    await message.answer("Раздел в разработке 🙂")
