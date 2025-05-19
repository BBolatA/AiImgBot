from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from ..keyboards.settings import main_settings_kb, format_kb

router = Router()


class SettingsStates(StatesGroup):
    menu = State()
    choosing_fmt = State()


async def _render_menu(target, state: FSMContext):
    data = await state.get_data()
    text = (
        "⚙️ <b>Настройки</b>\n\n"
        f"• Формат: <b>{data.get('fmt', '—').upper() if data.get('fmt') else '—'}</b>\n\n"
        "Выберите параметр для изменения:"
    )
    markup = main_settings_kb()
    if isinstance(target, Message):
        await target.answer(text, parse_mode="HTML", reply_markup=markup)
    else:
        await target.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
        await target.answer()


@router.callback_query(F.data == "settings:open")
async def settings_open(cb: CallbackQuery, state: FSMContext):
    await _render_menu(cb, state)
    await state.set_state(SettingsStates.menu)


@router.callback_query(F.data == "chg_fmt")
async def menu_to_format(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text("Выберите формат:", reply_markup=format_kb())
    await state.set_state(SettingsStates.choosing_fmt)
    await cb.answer()


@router.callback_query(F.data.startswith("set_fmt:"))
async def on_format(cb: CallbackQuery, state: FSMContext):
    _, val = cb.data.split(":", 1)
    await state.update_data(fmt=val)
    await cb.answer("Формат сохранён ✔️")
    await _render_menu(cb, state)
    await state.set_state(SettingsStates.menu)
