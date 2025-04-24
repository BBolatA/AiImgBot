import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from .config import settings
from .routers import register


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(
        settings.tg_token,
        default=DefaultBotProperties(parse_mode="HTML")
    )

    dp = Dispatcher(storage=MemoryStorage())
    register(dp)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
