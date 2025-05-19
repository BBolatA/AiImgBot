import logging
import asyncio
from uuid import uuid4
from typing import List

import aiohttp
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BufferedInputFile,
    InputMediaPhoto,
    CallbackQuery,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..services.backend import create_task, wait_ready

logger = logging.getLogger(__name__)
router = Router()

DEFAULT_STYLE_LIST: list[str] = []
DEFAULT_MODEL = ""


@router.message(Command("img"))
async def ask_qty(message: types.Message, state: FSMContext):
    prompt = message.text.removeprefix("/img").strip()
    if not prompt:
        return await message.answer("❗️После /img напишите текст запроса.")

    pid = uuid4().hex
    data = await state.get_data()
    jobs = data.get("jobs", {})
    jobs[pid] = {"prompt": prompt}
    await state.update_data(jobs=jobs)

    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        builder.button(text=str(i), callback_data=f"auto_qty:{i}:{pid}")
    builder.adjust(5)

    await message.answer(
        f"🔢 Сколько картинок сгенерировать?\n<code>{prompt}</code>",
        reply_markup=builder.as_markup(),
    )


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


@router.callback_query(F.data.startswith("auto_qty:"))
async def on_auto_qty(callback: CallbackQuery, state: FSMContext):
    _, qty_str, pid = callback.data.split(":", 2)
    if not qty_str.isdigit():
        return await callback.answer("❗️Некорректное количество.", show_alert=True)
    qty = int(qty_str)

    data = await state.get_data()
    job = data.get("jobs", {}).get(pid)
    if not job:
        return await callback.answer("❗️Сессия устарела.", show_alert=True)

    prompt = job["prompt"]
    fmt = data.get("fmt")

    await callback.answer("Генерируем ⏳")
    await callback.message.edit_text(
        f"🖌 Генерируем <b>{qty}</b> изображений…"
    )

    try:
        task_id = await create_task(
            prompt,
            callback.message.chat.id,
            qty,
            DEFAULT_STYLE_LIST,
            DEFAULT_MODEL,
            save_extension=fmt,
        )
        urls = await wait_ready(task_id, callback.message.chat.id)
        files = await _download_files(urls)
    except Exception as e:
        logger.exception("Generation error")
        return await callback.message.answer(f"⚠️ Ошибка генерации: {e}")

    if len(files) == 1:
        await callback.message.answer_photo(files[0])
    else:
        media = [InputMediaPhoto(media=f) for f in files]
        await callback.message.answer_media_group(media)
