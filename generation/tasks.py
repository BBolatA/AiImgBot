import base64
import binascii
import logging
import requests

from django.conf import settings
from django.core.files.base import ContentFile

from .models import GenerationTask, GeneratedImage
from .fooocus_client import FooocusClient
from imgbot.celery import app

logger = logging.getLogger(__name__)
client = FooocusClient(settings.FOOOCUS_HOST)


@app.task(name="generation.tasks.run_generation")
def run_generation(task_id: int) -> None:
    task = GenerationTask.objects.get(pk=task_id)
    task.status = "STARTED"
    task.save(update_fields=["status"])

    try:
        qty = getattr(task, "qty", 1) or 1
        style_selections = getattr(task, "style_selections", None) or ["Fooocus V2", "Fooocus Masterpiece"]
        base_model = getattr(task, "base_model_name", "") or ""

        result = client.text2img(
            task.prompt,
            qty,
            style_selections=style_selections,
            base_model_name=base_model,
            require_base64=True
        )

        if not isinstance(result, list) or not result:
            raise ValueError("Fooocus вернул пустой список")

        for idx, item in enumerate(result):
            raw_bytes = None

            if isinstance(item, dict) and item.get("base64"):
                b64 = item["base64"].split(",", 1)[-1]
                try:
                    raw_bytes = base64.b64decode(b64 + "===")
                except binascii.Error:
                    raw_bytes = None

            if raw_bytes is None and isinstance(item, dict) and item.get("url"):
                resp = requests.get(item["url"], timeout=60)
                if resp.ok:
                    raw_bytes = resp.content

            if raw_bytes is None:
                logger.warning("Task %s: item %s не распознан", task_id, idx)
                continue

            gi = GeneratedImage(task=task, index=idx)
            gi.image.save(f"{task_id}_{idx}.png", ContentFile(raw_bytes), save=False)
            gi.save()

        task.status = "READY" if task.images.exists() else "ERROR"

    except Exception:
        logger.exception("Ошибка генерации для task %s", task_id)
        task.status = "ERROR"
        raise

    finally:
        task.save(update_fields=["status"])
