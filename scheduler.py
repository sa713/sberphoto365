import asyncio
from aiogram import Bot
from datetime import datetime, timedelta, time as dtime
from config import DATABASE_PATH, CHANNEL_ID, PUBLISH_HOUR, PUBLISH_MINUTE
import sqlite3

async def publish_daily_summary(bot: Bot):
    now = datetime.now()
    summary_date = (now - timedelta(days=2)).date()  # Сводка за позавчера

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT username, file_id, upvotes, downvotes
        FROM photos
        WHERE shot_date = ?
    """, (str(summary_date),))
    rows = c.fetchall()
    conn.close()

    if not rows:
        await bot.send_message(CHANNEL_ID, f"📊 Сводка за {summary_date}:\nНет загруженных фотографий.")
        return

    sorted_rows = sorted(rows, key=lambda r: r[2], reverse=True)  # сортировка по upvotes
    top_score = sorted_rows[0][2]

    winners = [r for r in sorted_rows if r[2] == top_score and top_score > 0]
    summary_lines = [f"📅 Сводка за {summary_date}"]

    for username, _, up, down in sorted_rows:
        summary_lines.append(f"@{username}: 👍 {up} | 🤔 {down}")

    if winners:
        authors = ", ".join(f"@{r[0]}" for r in winners)
        await bot.send_message(CHANNEL_ID, "\n".join(summary_lines) + f"\n🏆 Победа: {authors}")
        for _, file_id, _, _ in winners:
            await bot.send_photo(CHANNEL_ID, file_id)
    else:
        await bot.send_message(CHANNEL_ID, "\n".join(summary_lines) + "\n❌ Нет победителей (0 голосов).")

async def wait_until_target_time():
    while True:
        now = datetime.now()
        target = datetime.combine(now.date(), dtime(PUBLISH_HOUR, PUBLISH_MINUTE))
        if now >= target:
            target += timedelta(days=1)
        wait_time = (target - now).total_seconds()
        await asyncio.sleep(wait_time)
        yield

async def setup_scheduler(bot: Bot):
    asyncio.create_task(run_scheduler(bot))

async def run_scheduler(bot: Bot):
    async for _ in wait_until_target_time():
        await publish_daily_summary(bot)
