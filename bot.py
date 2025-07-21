import asyncio
from aiogram import Bot, Dispatcher, F
from handlers import router
from config import BOT_TOKEN
from scheduler import setup_scheduler

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await setup_scheduler(bot)

    try:
        print("🚀 Бот запускается...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
