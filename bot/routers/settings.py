from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from ..keyboards.settings import resolution_kb, quality_kb, format_kb
from ..keyboards.menu import main_menu

router = Router()


class SettingsStates(StatesGroup):
    choosing_res = State()
    choosing_q = State()
    choosing_fmt = State()


@router.message(F.text == "⚙️  Настройки")
async def cmd_settings(message: Message, state: FSMContext):
    await message.answer("Выберите разрешение:", reply_markup=resolution_kb())
    await state.set_state(SettingsStates.choosing_res)


@router.callback_query(F.data.startswith("set_res:"))
async def on_res(callback: CallbackQuery, state: FSMContext):
    _, val = callback.data.split(":", 1)
    await state.update_data(resolution=val)
    await callback.message.edit_text(
        f"Разрешение выбрано: <b>{val.replace('*','×')}</b>\nТеперь выберите качество:",
        parse_mode="HTML",
        reply_markup=quality_kb()
    )
    await state.set_state(SettingsStates.choosing_q)


@router.callback_query(F.data.startswith("set_q:"))
async def on_quality(callback: CallbackQuery, state: FSMContext):
    _, val = callback.data.split(":", 1)
    await state.update_data(quality=val)
    await callback.message.edit_text(
        f"Качество выбрано: <b>{val}</b>\nИ, наконец, выберите формат:",
        parse_mode="HTML",
        reply_markup=format_kb()
    )
    await state.set_state(SettingsStates.choosing_fmt)


@router.callback_query(F.data.startswith("set_fmt:"))
async def on_format(callback: CallbackQuery, state: FSMContext):
    _, val = callback.data.split(":", 1)
    await state.update_data(fmt=val)
    data = await state.get_data()
    text = (
        f"✅ Настройки сохранены:\n"
        f"• Разрешение: <b>{data['resolution'].replace('*','×')}</b>\n"
        f"• Качество: <b>{data['quality']}</b>\n"
        f"• Формат: <b>{data['fmt']}</b>"
    )
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.message.answer("Выберите действие:", reply_markup=main_menu(callback.from_user.id))
    await state.set_state(None)
