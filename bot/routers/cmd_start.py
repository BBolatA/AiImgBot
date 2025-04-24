from aiogram import Router, types
from aiogram.filters import Command

router = Router()


@router.message(Command("start", "help"))
async def start(message: types.Message):
    await message.answer(
        'Привет! Отправь\n'
        '<code>/img кот в очках</code>\n'
        'и выбери, сколько картинок сгенерировать.'
    )
