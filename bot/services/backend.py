import asyncio
import aiohttp
import hmac
import hashlib
from typing import List

from bot.config import settings


def _bot_sig(chat_id: int) -> str:
    secret = settings.bot_internal_token.encode()
    return hmac.new(secret, str(chat_id).encode(), hashlib.sha256).hexdigest()


def _auth_headers(chat_id: int) -> dict[str, str]:
    return {
        "X-Bot-Token": _bot_sig(chat_id),
        "X-Chat-Id":   str(chat_id),
    }


async def create_task(
    prompt: str,
    chat_id: int,
    qty: int,
    style_selections: list[str] | None = None,
    base_model_name: str | None = None,
    performance_selection: str | None = None,
    aspect_ratios_selection: str | None = None,
    save_extension: str | None = None,
) -> int:
    payload: dict = {
        "query": prompt,
        "tg_chat_id": chat_id,
        "qty": qty,
    }

    if style_selections:
        payload["style_selections"] = style_selections
    if base_model_name:
        payload["base_model_name"] = base_model_name
    if performance_selection:
        payload["performance_selection"] = performance_selection
    if aspect_ratios_selection:
        payload["aspect_ratios_selection"] = aspect_ratios_selection
    if save_extension:
        payload["save_extension"] = save_extension

    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            f"{settings.backend_url}/api/v1/generation/generate/",
            json=payload,
            headers=_auth_headers(chat_id),
        )
        body = await resp.text()
        if resp.status != 201:
            raise RuntimeError(f"backend {resp.status}: {body}")
        data = await resp.json()
        return data["task_id"]


async def wait_ready(task_id: int, chat_id: int) -> List[str]:
    timeout = aiohttp.ClientTimeout(total=1800)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        while True:
            await asyncio.sleep(2)
            async with session.get(
                f"{settings.backend_url}/api/v1/generation/status/{task_id}/",
                headers=_auth_headers(chat_id),
            ) as resp:
                if resp.status == 403:
                    raise RuntimeError("backend 403 — аутентификация не прошла")
                data = await resp.json()
                status = data.get("status")
                if status == "READY":
                    return [
                        settings.backend_url + img["image"]
                        for img in data.get("images", [])
                    ]
                if status == "ERROR":
                    raise RuntimeError("Backend вернул status=ERROR")
