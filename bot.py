import asyncio
from aiogram import Bot, Dispatcher
from handlers import router
from scheduler import setup_scheduler
import config
import database

async def main():
    database.init_db()
    bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(router)

    setup_scheduler(bot)

    print("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())