import uuid
import base64
import binascii
import logging
import random
from pathlib import Path
from datetime import timedelta

import requests

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone as tz

from .models import GenerationTask, GeneratedImage
from core.services.fooocus_client import FooocusClient
from core.services.agent import load_styles

from celery.schedules import crontab
from imgbot.celery import app
from generation.models import DailyPrompt


logger = logging.getLogger(__name__)
client = FooocusClient(settings.FOOOCUS_HOST)
PROMPTS = [p.strip() for p in Path("prompts.txt").read_text().splitlines() if p.strip()]


@app.task(name="generation.tasks.run_generation")
def run_generation(task_id: int) -> None:
    task = GenerationTask.objects.get(pk=task_id)
    task.status = "STARTED"
    task.save(update_fields=["status"])

    try:
        qty = task.qty or 1
        style_selections = task.style_selections or ["Fooocus V2", "Fooocus Masterpiece"]
        base_model = task.base_model_name or ""
        perf = task.performance_selection or None
        ar = task.aspect_ratios_selection or None
        ext = task.save_extension or None
        style_meta = load_styles().get(style_selections[0]) if style_selections else None
        pos_prompt = (
            style_meta["prompt"].format(prompt=task.prompt) if style_meta else task.prompt
        )
        neg_prompt = style_meta.get("negative_prompt", "") if style_meta else ""
        kwargs = dict(
            prompt=pos_prompt,
            qty=qty,
            style_selections=style_selections,
            base_model_name=base_model,
            performance_selection=perf,
            aspect_ratios_selection=ar,
            save_extension=ext,
            require_base64=True,
        )
        if neg_prompt:
            kwargs["negative_prompt"] = neg_prompt

        try:
            result = client.text2img(**kwargs)
        except TypeError as e:
            if "negative_prompt" in str(e):
                logger.warning(
                    "FooocusClient.text2img() не поддерживает negative_prompt – повтор без него"
                )
                kwargs.pop("negative_prompt", None)
                result = client.text2img(**kwargs)
            else:
                raise

        if not isinstance(result, list) or not result:
            raise ValueError("Fooocus вернул пустой список")

        task.images.all().delete()

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

            filename = f"{uuid.uuid4().hex}.{ext or 'png'}"
            GeneratedImage.objects.create(
                task=task,
                image=ContentFile(raw_bytes, name=filename),
                index=idx,
            )

        task.status = "READY" if task.images.exists() else "ERROR"

    except Exception:
        logger.exception("Ошибка генерации для task %s", task_id)
        task.status = "ERROR"
        raise

    finally:
        task.save(update_fields=["status"])


@app.task(name="generation.tasks.generate_image")
def generate_image(task_id: int) -> None:
    task = GenerationTask.objects.get(pk=task_id)
    task.status = "STARTED"
    task.save(update_fields=["status"])

    try:
        styles = task.style_selections or ["Fooocus V2", "Fooocus Masterpiece"]
        model = task.base_model_name or ""
        perf = task.performance_selection or None
        ar = task.aspect_ratios_selection or None
        ext = task.save_extension or None

        result = client.text2img(
            task.prompt,
            task.qty,
            style_selections=styles,
            base_model_name=model,
            require_base64=False,
            performance_selection=perf,
            aspect_ratios_selection=ar,
            save_extension=ext,
        )

        if not isinstance(result, list) or not result:
            raise ValueError("Fooocus вернул пустой список")

        task.images.all().delete()

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

            filename = f"{uuid.uuid4().hex}.{ext or 'png'}"
            GeneratedImage.objects.create(
                task=task,
                image=ContentFile(raw_bytes, name=filename),
                index=idx
            )

        task.status = "READY" if task.images.exists() else "ERROR"

    except Exception:
        task.status = "ERROR"
        logger.exception("Ошибка генерации для task %s", task_id)
        raise

    finally:
        task.save(update_fields=["status"])


@app.on_after_finalize.connect
def setup_daily_prompt(sender, **_):
    sender.add_periodic_task(
        crontab(hour=2, minute=0),
        create_prompt_of_day.s(),
        name="daily_prompt",
    )


@app.task
def create_prompt_of_day():
    if not PROMPTS:
        return
    tomorrow = tz.localdate() + timedelta(days=1)
    if DailyPrompt.objects.filter(date=tomorrow).exists():
        return
    text = random.choice(PROMPTS)
    emoji = "💡"
    DailyPrompt.objects.create(date=tomorrow, emoji=emoji, prompt=text)
