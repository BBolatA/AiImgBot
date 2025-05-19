import json, pathlib, functools, openai, numpy as np
from django.conf import settings
from .model_alias import MODEL_ALIAS
from openai import embeddings


@functools.lru_cache
def load_styles() -> dict[str, dict]:
    styles = {}
    styles_dir = pathlib.Path(settings.BASE_DIR) / "styles"
    for p in styles_dir.glob("*.json"):
        for s in json.loads(p.read_text()):
            styles[s["name"]] = s
    return styles


STYLE_REGISTRY = load_styles()
STYLE_NAMES = list(STYLE_REGISTRY.keys())
ALLOWED_MODELS = list(MODEL_ALIAS.keys())
ALLOWED_RES = ["1152*896", "1280*768", "1024*1024", "768*1280", "896*1152"]

sys_prompt = (
    "Ты — главный арт-директор нейросети.\n\n"

    "Верни СТРОГО JSON-объект:\n"
    "  • \"prompt\"      – развёрнутый positive-prompt (английский, ≥ 7-10 слов).\n"
    "  • \"style\"       – строка / список строк из перечня стилей.\n"
    "  • \"model\"       – juggernaut-xl | ghost-xl | anima-pencil.\n"
    "  • \"resolution\"  – одно значение из: 1152*896, 1280*768, 1024*1024, "
    "768*1280, 896*1152.\n\n"

    "Как выбирать модель и писать prompt:\n"
    "  • juggernaut-xl  → фотореализм, сочные concept-art сцены.\n"
    "    Формула prompt-a:  \n"
    "      \"<subject>, <environment / background>, "
    "<camera or lens>, <lighting>, <style adjectives>, ultra detailed\"\n"
    "    Пример:  \n"
    "      \"Portrait of a futurist knight, ruined cathedral background, "
    "50 mm photo, dramatic rim light, cinematic, ultra detailed\"\n"
    "  • ghost-xl       → полу-реалистичное аниме / ghost-mix. "
    "Лучше всего работает с *art style* ключами "
    "(пример: \"illustration art style\", \"realistic art style\"). "
    "Рекомендованы разрешения 1024-1536 px.\n"
    "  • anima-pencil   → чистые аниме-иллюстрации, яркие линии и контуры.\n\n"

    f"Стили: {', '.join(STYLE_NAMES)}.\n"
    f"Разрешения: {', '.join(ALLOWED_RES)}.\n"
    "Модель указывай ровно этими id (без .safetensors).\n\n"
    "Пользователь может писать на любом языке — сначала переведи ключевые "
    "слова на английский, затем создай «prompt» по правилам.\n"
    "Никаких комментариев вне JSON!"
)


@functools.lru_cache
def _style_embeddings() -> tuple[np.ndarray, list[str]]:
    vecs, names = [], []
    for name, meta in STYLE_REGISTRY.items():
        descr = (
            meta.get("prompt")
            or meta.get("positive_prompt")
            or meta.get("description")
            or ""
        )
        seed = f"{name.replace('-', ' ')} {descr.split('{prompt}')[0]}".strip() or name
        vec = embeddings.create(model="text-embedding-3-small", input=seed).data[0].embedding
        vecs.append(vec)
        names.append(name)
    return np.array(vecs), names


def nearest_style(text: str) -> str:
    q = openai.embeddings.create(model="text-embedding-3-small", input=text).data[0].embedding
    embs, names = _style_embeddings()
    return names[int(np.argmax(embs @ np.array(q)))]


def generate(query: str) -> dict:
    rsp = openai.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": query},
        ],
    )
    return json.loads(rsp.choices[0].message.content)