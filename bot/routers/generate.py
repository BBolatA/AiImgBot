import logging
import asyncio
from uuid import uuid4
from typing import List, Dict

import aiohttp
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BufferedInputFile,
    InputMediaPhoto,
    CallbackQuery,
    InlineKeyboardMarkup,
)
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..services.backend import create_task, wait_ready

logger = logging.getLogger(__name__)
router = Router()

STYLE_OPTIONS: Dict[str, str] = {
    "sai": "SAI Anime",
    "mre": "MRE Elemental Art",
    "rococo": "Neo Rococo",
    "dream": "Misc Dreamscape",
}

MODEL_MAP: Dict[str, str] = {
    "sai": "animaPencilXL_v100.safetensors",
    "mre": "ghostxl_v10BakedVAE.safetensors",
    "rococo": "ghostxl_v10BakedVAE.safetensors",
    "dream": "juggernautXL_juggXIByRundiffusion.safetensors",
}

DEFAULT_STYLES = ["Fooocus V2", "Fooocus Masterpiece"]


@router.message(Command("img"))
async def ask_style(message: types.Message, state: FSMContext):
    prompt = message.text.removeprefix("/img").strip()
    if not prompt:
        return await message.answer("❗️После /img напишите текст запроса.")

    pid = uuid4().hex
    data = await state.get_data()
    jobs = data.get("jobs", {})
    jobs[pid] = {"prompt": prompt}
    await state.update_data(jobs=jobs)

    builder = InlineKeyboardBuilder()
    for code, label in STYLE_OPTIONS.items():
        cb = f"style:{code}:{pid}"
        builder.button(text=label, callback_data=cb)
    builder.adjust(2)

    await message.answer(
        f"🎨 Выберите стиль для запроса:\n<code>{prompt}</code>",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data.startswith("style:"))
async def on_style_pick(callback: CallbackQuery, state: FSMContext):
    _, style_code, pid = callback.data.split(":", 2)
    data = await state.get_data()
    jobs = data.get("jobs", {})
    job = jobs.get(pid)
    if not job:
        return await callback.answer("❗️Сессия не найдена.", show_alert=True)

    job["style"] = style_code
    await state.update_data(jobs=jobs)
    await callback.answer(f"Стиль: {STYLE_OPTIONS[style_code]}")

    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        cb = f"qty:{i}:{pid}:{style_code}"
        builder.button(text=str(i), callback_data=cb)
    builder.adjust(5)

    await callback.message.edit_text(
        f"🔢 Сколько картинок ({STYLE_OPTIONS[style_code]}) сгенерировать?",
        reply_markup=builder.as_markup()
    )


async def _safe_edit_markup(msg: types.Message, markup: InlineKeyboardMarkup):
    try:
        await msg.edit_reply_markup(reply_markup=markup)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            return
        raise


async def _download_files(urls: List[str]) -> List[BufferedInputFile]:
    async def _fetch(session, url, idx):
        async with session.get(url) as resp:
            resp.raise_for_status()
            data = await resp.read()
            return BufferedInputFile(data, filename=f"img_{idx}.png")

    timeout = aiohttp.ClientTimeout(total=120)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [_fetch(session, u, i) for i, u in enumerate(urls)]
        return await asyncio.gather(*tasks)


@router.callback_query(F.data.startswith("qty:"))
async def on_qty_pick(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":", 3)
    if len(parts) != 4:
        return await callback.answer("❗️Некорректные данные.", show_alert=True)
    _, qty_str, pid, style_code = parts
    if not qty_str.isdigit():
        return await callback.answer("❗️Некорректное количество.", show_alert=True)
    qty = int(qty_str)

    data = await state.get_data()
    job = data.get("jobs", {}).get(pid)
    if not job or job.get("style") != style_code:
        return await callback.answer("❗️Сессия устарела.", show_alert=True)

    prompt = job["prompt"]
    style_label = STYLE_OPTIONS[style_code]
    model_name = MODEL_MAP.get(style_code, "animaPencilXL_v100.safetensors")

    await callback.answer("Генерируем ⏳")
    await callback.message.edit_text(
        f"🖌 Генерируем <b>{qty}</b> изображений в стиле <b>{style_label}</b>…"
    )

    style_selections = DEFAULT_STYLES + [style_label]
    base_model_name = model_name
    settings_data = await state.get_data()
    perf = settings_data.get("quality")
    ar = settings_data.get("resolution")
    fmt = settings_data.get("fmt")
    try:
        task_id = await create_task(
            prompt,
            callback.message.chat.id,
            qty,
            style_selections,
            base_model_name,
            performance_selection=perf,
            aspect_ratios_selection=ar,
            save_extension=fmt,
        )
        urls = await wait_ready(task_id)
        files = await _download_files(urls)
    except Exception as e:
        logger.exception("Generation error")
        return await callback.message.answer(f"⚠️ Ошибка генерации: {e}")

    if len(files) == 1:
        sent_list = [await callback.message.answer_photo(files[0])]
    else:
        media = [InputMediaPhoto(media=f) for f in files]
        sent_list = await callback.message.answer_media_group(media)
    sent = sent_list[0]

    builder = InlineKeyboardBuilder()
    retry_cb = f"retry:{pid}:{style_code}"
    delete_cb = "delete"
    builder.button(text="🔄 Retry", callback_data=retry_cb)
    builder.button(text="🗑 Delete", callback_data=delete_cb)
    builder.adjust(2)
    await _safe_edit_markup(sent, builder.as_markup())


@router.callback_query(F.data.startswith("retry:"))
async def on_retry(callback: CallbackQuery, state: FSMContext):
    _, pid, style_code = callback.data.split(":", 2)
    data = await state.get_data()
    job = data.get("jobs", {}).get(pid)
    if not job or job.get("style") != style_code:
        return await callback.answer("❗️Сессия не найдена.", show_alert=True)

    prompt = job["prompt"]
    model_name = MODEL_MAP.get(style_code, "animaPencilXL_v100.safetensors")
    style_selections = DEFAULT_STYLES + [STYLE_OPTIONS[style_code]]

    # вот эти три — из state
    perf = data.get("quality")
    ar   = data.get("resolution")
    fmt  = data.get("fmt")

    await callback.answer("Повторяем…")

    try:
        task_id = await create_task(
            prompt,
            callback.message.chat.id,
            1,
            style_selections,
            model_name,
            performance_selection=perf,
            aspect_ratios_selection=ar,
            save_extension=fmt,
        )
        urls = await wait_ready(task_id)
        files = await _download_files(urls)
    except Exception as e:
        logger.exception("Retry error")
        return await callback.message.answer(f"⚠️ Ошибка retry: {e}")

    if files:
        await callback.message.answer_photo(files[0])


@router.callback_query(F.data == "delete")
async def on_delete(callback: CallbackQuery):
    await callback.answer("Удалено 🗑")
    try:
        await callback.message.delete()
    except:
        pass
