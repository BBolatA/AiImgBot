import asyncio

import aiohttp
from bot.config import settings


async def create_task(
    prompt: str,
    chat_id: int,
    qty: int,
    style_selections: list[str],
    base_model_name: str
) -> int:
    payload = {
        'prompt': prompt,
        'tg_chat_id': chat_id,
        'qty': qty,
        'style_selections': style_selections,
        'base_model_name': base_model_name,
    }

    async with aiohttp.ClientSession() as session:
        response = await session.post(
            f"{settings.backend_url}/api/generate/",
            json=payload
        )
        response.raise_for_status()
        data = await response.json()
        return data['task_id']


async def wait_ready(task_id: int) -> list[str]:
    async with aiohttp.ClientSession() as session:
        while True:
            await asyncio.sleep(2)
            async with session.get(f"{settings.backend_url}/api/status/{task_id}/") as r:
                data = await r.json()
                if data.get("status") == "READY":
                    return [settings.backend_url + img["image"] for img in data["images"]]
                if data.get("status") == "ERROR":
                    raise RuntimeError("Backend вернул status=ERROR")
