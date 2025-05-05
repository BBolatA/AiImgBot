from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from ..keyboards.settings import (
    main_settings_kb, resolution_kb, quality_kb,
    format_kb, model_kb, MODELS,
)

router = Router()


class SettingsStates(StatesGroup):
    menu = State()
    choosing_res = State()
    choosing_q = State()
    choosing_fmt = State()
    choosing_model = State()


async def _render_menu(target, state: FSMContext):
    data = await state.get_data()

    def fmt_model(key):
        return MODELS.get(key, {}).get("name", key) if key else "—"

    text = (
        "⚙️ <b>Текущие настройки</b>\n"
        f"• Разрешение: <b>{data.get('resolution', '—').replace('*','×')}</b>\n"
        f"• Качество: <b>{data.get('quality', '—')}</b>\n"
        f"• Формат: <b>{data.get('fmt', '—').upper() if data.get('fmt') else '—'}</b>\n"
        f"• Модель: <b>{fmt_model(data.get('model'))}</b>\n\n"
        "Выберите параметр для изменения:"
    )

    if isinstance(target, Message):
        await target.answer(text, parse_mode="HTML",
                            reply_markup=main_settings_kb())
    else:  # CallbackQuery
        await target.message.edit_text(text, parse_mode="HTML",
                                       reply_markup=main_settings_kb())
        await target.answer()


@router.callback_query(F.data == "settings:open")
async def settings_open(call: CallbackQuery, state: FSMContext):
    await _render_menu(call, state)
    await state.set_state(SettingsStates.menu)


@router.callback_query(F.data == "chg_res")
async def menu_to_res(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text("Выберите разрешение:",
                               reply_markup=resolution_kb())
    await state.set_state(SettingsStates.choosing_res)
    await cb.answer()


@router.callback_query(F.data == "chg_q")
async def menu_to_quality(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text("Выберите качество:",
                               reply_markup=quality_kb())
    await state.set_state(SettingsStates.choosing_q)
    await cb.answer()


@router.callback_query(F.data == "chg_fmt")
async def menu_to_format(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text("Выберите формат:", reply_markup=format_kb())
    await state.set_state(SettingsStates.choosing_fmt)
    await cb.answer()


@router.callback_query(F.data == "chg_model")
async def menu_to_model(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text("Выберите модель:", reply_markup=model_kb())
    await state.set_state(SettingsStates.choosing_model)
    await cb.answer()


@router.callback_query(F.data.startswith("set_res:"))
async def on_res(cb: CallbackQuery, state: FSMContext):
    _, val = cb.data.split(":", 1)
    await state.update_data(resolution=val)
    await cb.answer("Разрешение сохранено ✔️")
    await _render_menu(cb, state)
    await state.set_state(SettingsStates.menu)


@router.callback_query(F.data.startswith("set_q:"))
async def on_quality(cb: CallbackQuery, state: FSMContext):
    _, val = cb.data.split(":", 1)
    await state.update_data(quality=val)
    await cb.answer("Качество сохранено ✔️")
    await _render_menu(cb, state)
    await state.set_state(SettingsStates.menu)


@router.callback_query(F.data.startswith("set_fmt:"))
async def on_format(cb: CallbackQuery, state: FSMContext):
    _, val = cb.data.split(":", 1)
    await state.update_data(fmt=val)
    await cb.answer("Формат сохранён ✔️")
    await _render_menu(cb, state)
    await state.set_state(SettingsStates.menu)


@router.callback_query(F.data.startswith("set_model:"))
async def on_model(cb: CallbackQuery, state: FSMContext):
    _, val = cb.data.split(":", 1)
    await state.update_data(model=val)
    await cb.answer("Модель сохранена ✔️")
    await _render_menu(cb, state)
    await state.set_state(SettingsStates.menu)


@router.callback_query(F.data.startswith("model_info:"))
async def on_model_info(cb: CallbackQuery):
    _, key = cb.data.split(":", 1)
    cfg = MODELS.get(key)
    if not cfg:
        return await cb.answer("Неизвестная модель", show_alert=True)

    text = (
        f"<b>{cfg['name']}</b>\n\n"
        f"{cfg['description']}\n\n"
        "💡 Пример промпта:\n"
        f"<code>{cfg['example_prompt']}</code>"
    )
    await cb.message.answer(text, parse_mode="HTML")
    await cb.answer()
