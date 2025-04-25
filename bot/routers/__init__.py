from aiogram import Dispatcher
from .cmd_start import router as start_router
from .menu import router as menu_router
from .generate import router as gen_router
from .settings import router as settings_router


def register(dp: Dispatcher):
    dp.include_router(menu_router)
    dp.include_router(start_router)
    dp.include_router(settings_router)
    dp.include_router(gen_router)
