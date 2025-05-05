from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

# ── модели с описаниями и примером ─────────────────────────────
MODELS = {
    "animaPencilXL_v100.safetensors": {
        "name": "Anime Pencil XL",
        "description": "Чёткие штрихи и выразительные линии. "
                       "Идеальна для персонажей в аниме-эстетике.",
        "example_prompt": "cute anime girl in city park, cinematic lighting",
    },
    "ghostxl_v10BakedVAE.safetensors": {
        "name": "Ghost XL v1 (VAE)",
        "description": "Полуреалистичная стилистика с мягкими тонами "
                       "и приятным глобальным освещением.",
        "example_prompt": "portrait of a knight in silver armor, delicate rim light",
    },
    "juggernautXL_juggXIByRundiffusion.safetensors": {
        "name": "Juggernaut XL v11",
        "description": "Фотореализм + сочные цвета. Подходит для "
                       "пейзажей и концепт-арта.",
        "example_prompt": "sunset over futuristic megacity skyline, ultra-detailed",
    },
}


def _builder_from_choices(prefix: str, choices, per_row: int = 3) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for text, val in choices:
        b.button(text=text, callback_data=f"{prefix}:{val}")
    b.adjust(per_row)
    return b.as_markup()


def resolution_kb() -> InlineKeyboardMarkup:
    choices = [
        ("1152×896", "1152*896"),
        ("1280×768", "1280*768"),
        ("1024×1024", "1024*1024"),
        ("768×1280", "768*1280"),
        ("896×1152", "896*1152"),
    ]
    return _builder_from_choices("set_res", choices, per_row=2)


def quality_kb() -> InlineKeyboardMarkup:
    choices = [
        ("Quality", "Quality"),
        ("Speed", "Speed"),
        ("Extreme Speed", "Extreme Speed"),
    ]
    return _builder_from_choices("set_q", choices)


def format_kb() -> InlineKeyboardMarkup:
    choices = [("PNG", "png"), ("JPEG", "jpeg"), ("WEBP", "webp")]
    return _builder_from_choices("set_fmt", choices)


def model_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for key, cfg in MODELS.items():
        b.button(text=cfg["name"], callback_data=f"set_model:{key}")
        b.button(text="ℹ️", callback_data=f"model_info:{key}")
    b.adjust(2)
    return b.as_markup()


def main_settings_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="Разрешение", callback_data="chg_res")
    b.button(text="Качество", callback_data="chg_q")
    b.button(text="Формат", callback_data="chg_fmt")
    b.button(text="Модель", callback_data="chg_model")
    b.adjust(2)
    return b.as_markup()
