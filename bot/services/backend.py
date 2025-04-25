import asyncio
import aiohttp
from bot.config import settings


async def create_task(
    prompt: str,
    chat_id: int,
    qty: int,
    style_selections: list[str],
    base_model_name: str,
    performance_selection: str | None = None,
    aspect_ratios_selection: str | None = None,
    save_extension: str | None = None,
) -> int:
    payload: dict = {
        'prompt': prompt,
        'tg_chat_id': chat_id,
        'qty': qty,
        'style_selections': style_selections,
        'base_model_name': base_model_name,
    }

    if performance_selection is not None:
        payload['performance_selection'] = performance_selection
    if aspect_ratios_selection is not None:
        payload['aspect_ratios_selection'] = aspect_ratios_selection
    if save_extension is not None:
        payload['save_extension'] = save_extension

    async with aiohttp.ClientSession() as session:
        response = await session.post(
            f"{settings.backend_url}/api/generate/",
            json=payload
        )
        await response.text()
        response.raise_for_status()
        data = await response.json()
        return data['task_id']


async def wait_ready(task_id: int) -> list[str]:
    async with aiohttp.ClientSession() as session:
        while True:
            await asyncio.sleep(2)
            async with session.get(f"{settings.backend_url}/api/status/{task_id}/") as r:
                data = await r.json()
                status = data.get("status")
                if status == "READY":
                    return [
                        settings.backend_url + img["image"]
                        for img in data.get("images", [])
                    ]
                if status == "ERROR":
                    raise RuntimeError("Backend вернул status=ERROR")
