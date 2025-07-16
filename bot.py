import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, LOG_FILE_PATH
from handlers import router
from scheduler import setup_scheduler

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, mode="w", encoding="utf-8")
        ]
    )

async def main():
    setup_logging()

    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(router)

    await setup_scheduler(bot)

    logging.info("Бот запущен.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
