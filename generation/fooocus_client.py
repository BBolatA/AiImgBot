import asyncio
import aiohttp
from django.conf import settings


class FooocusClient:
    def __init__(self, host: str | None = None):
        self.host = (host or settings.backend_url).rstrip('/')

    async def _post(self, route: str, payload: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.host}{route}",
                json=payload,
                timeout=300
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

    def text2img(
        self,
        prompt: str,
        qty: int = 1,
        style_selections: list[str] = None,
        base_model_name: str = "",
        require_base64: bool = True
    ) -> dict:
        if style_selections is None:
            style_selections = ["Fooocus V2", "Fooocus Masterpiece"]

        body = {
            "prompt": prompt,
            "image_number": qty,
            "image_seed": -1,
            "require_base64": require_base64,
            "async_process": False,
            "style_selections": style_selections,
            "base_model_name": base_model_name,
        }
        return asyncio.run(self._post("/v1/generation/text-to-image", body))
