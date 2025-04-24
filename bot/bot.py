import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, F
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('TG_TOKEN')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


async def poll_status(chat_id: int, task_id: int):
    async with aiohttp.ClientSession() as s:
        while True:
            await asyncio.sleep(2)
            async with s.get(f'{BACKEND_URL}/api/status/{task_id}/') as r:
                data = await r.json()
                if data['status'] == 'READY':
                    photo_url = BACKEND_URL + data['image']
                    await bot.send_photo(chat_id, photo_url)
                    break
                if data['status'] == 'ERROR':
                    await bot.send_message(chat_id, '⚠️ Ошибка генерации')
                    break


@dp.message(F.text.startswith('/img '))
async def handle_img(message):
    prompt = message.text[5:].strip()
    await message.answer('🖌 Генерирую, подождите…')

    async with aiohttp.ClientSession() as s:
        async with s.post(f'{BACKEND_URL}/api/generate/', json={
            'prompt': prompt,
            'tg_chat_id': message.chat.id
        }) as r:
            task_id = (await r.json())['task_id']

    await asyncio.create_task(poll_status(message.chat.id, task_id))

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))
