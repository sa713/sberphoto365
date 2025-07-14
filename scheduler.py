from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from datetime import datetime, date
import sqlite3
from config import TIMEZONE, PUBLISH_HOUR, CHANNEL_ID

def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)

    @scheduler.scheduled_job(CronTrigger(hour=PUBLISH_HOUR))
    async def publish_daily_summary():
        conn = sqlite3.connect("photo_challenge.db")
        c = conn.cursor()

        # День, за который считаем голосование (вчерашний)
        day_to_analyze = date.today() - timedelta(days=1)
        c.execute("""
            SELECT username, upvotes, downvotes, file_id
            FROM photos
            WHERE submission_date = ? 
            ORDER BY upvotes DESC, downvotes ASC
        """, (str(day_to_analyze),))
        rows = c.fetchall()

        if not rows:
            await bot.send_message(CHANNEL_ID, f"📊 Нет фотографий за {day_to_analyze}")
            return

        # Текстовая сводка
        text_lines = [f"📊 Результаты голосования за {day_to_analyze}:"]
        for row in rows:
            username, up, down, _ = row
            text_lines.append(f"@{username} — 👍 {up} / 👎 {down}")
        text = "\n".join(text_lines)

        await bot.send_message(CHANNEL_ID, text)

        # Фото победителя
        best = rows[0]
        best_file_id = best[3]
        await bot.send_photo(CHANNEL_ID, best_file_id, caption="🏆 Фото дня по итогам голосования!")

        conn.close()

    scheduler.start()