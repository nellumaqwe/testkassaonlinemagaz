import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from botapp.handlers import router
from botapp.cart_handlers import cart_router
from botapp.user_handlers import user_router
from botapp.orders_handlers import orders_router
from botapp.config import settings
from botapp.db.database import init_db

async def on_startup():
    try:
        await init_db()
        logging.info("Database initialized")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        raise

async def main():
    dp = Dispatcher()
    
    # Инициализация базы данных перед стартом
    await on_startup()
    
    dp.include_router(user_router)
    dp.include_router(router)
    dp.include_router(cart_router)
    dp.include_router(orders_router)
    bot = Bot(token=settings["TOKEN"], 
             default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())