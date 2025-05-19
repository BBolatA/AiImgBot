# AI-Image-Bot

Telegram-бот, который превращает текстовые запросы в готовые изображения  
( Fooocus / SDXL + LLM-агент **GPT-4o-mini** ).

👉 **Попробовать вживую:** [@devaimgbot](https://t.me/devaimgbot)

* Пользователь пишет `/img …` на любом языке.  
* Агент автоматически  
  1. переводит запрос на английский и расширяет его до **positive-prompt**;  
  2. выбирает художественный **стиль**, **модель** и **разрешение**;  
* Пользователь задаёт **кол-во** картинок (1–5) и **формат** (PNG / JPEG / WEBP) — и получает результат.

---
## Стек

| Подсистема   | Технологии                                   |
|--------------|----------------------------------------------|
| Telegram-бот | **Aiogram 3** · FSM                          |
| API          | Django 5 · DRF                               |
| Генерация    | Celery · Redis · **Fooocus v2**              |
| LLM-агент    | OpenAI (GPT-4o-mini + embeddings v3)         |

---
## Локальный запуск

```bash
git clone https://github.com/BBolatA/AiImgBot.git
cd AiImgBot

python -m venv .venv
.venv\Scripts\activate            
pip install -r requirements.txt

cp .env.example .env              

python manage.py migrate

# ── запуск ──
python manage.py runserver         
celery -A imgbot worker -l info  
celery -A imgbot beat   -l info    
python -m bot                      
