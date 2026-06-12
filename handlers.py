from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatType, ContentType
from datetime import datetime, timedelta
import sqlite3
import logging
import uuid

from config import CHANNEL_ID, DATABASE_PATH, CHAT_ID, CHALLENGE_START_DATE

router = Router()


@router.message(F.text == "/start")
async def cmd_start(message: Message):
    logging.info("👋 Команда /start от %s", message.from_user.id)
    await message.answer(
        "👋 Привет! Это бот фото-челленджа 365.\n"
        "Отправь мне фотографию, и я помогу опубликовать её.\n"
        "Суть челленджа - снимать каждый день на протяжении года (365 дней). Я буду считать длительность серии и указывать её в постах. А ещё за каждый день буду публиковать снимки с наибольшим количеством лайков.\n"
        "Удачи!"
    )


@router.message(F.text == "/test")
async def test(message: Message):
    await message.answer("✅ Бот работает!")


@router.message(F.chat.type == ChatType.PRIVATE, F.content_type == ContentType.PHOTO)
async def handle_photo(message: Message):
    bot = message.bot
    user_id = message.from_user.id
    file_id = message.photo[-1].file_id

    try:
        member = await bot.get_chat_member(chat_id=CHAT_ID, user_id=user_id)
        if member.status in ("left", "kicked"):
            await message.reply("❌ Вы должны быть участником чата, чтобы участвовать в челлендже.")
            return
    except Exception:
        await message.reply("⚠️ Не удалось проверить ваш статус в чате.")
        return

    short_id = str(uuid.uuid4())[:8]

    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO temp_photos (short_id, file_id) VALUES (?, ?)",
        (short_id, file_id)
    )
    conn.commit()
    conn.close()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 Сегодня", callback_data=f"date:today:{short_id}"),
            InlineKeyboardButton(text="📆 Вчера", callback_data=f"date:yesterday:{short_id}")
        ],
        [InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel:{short_id}")]
    ])
    await message.reply("Выбери дату съёмки фотографии:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("date:"))
async def process_date_choice(callback_query: CallbackQuery):
    bot = callback_query.bot
    _, choice, short_id = callback_query.data.split(":")
    user = callback_query.from_user
    user_id = user.id
    username = user.username or f"user{user_id}"

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT file_id FROM temp_photos WHERE short_id = ?", (short_id,))
    row = c.fetchone()
    if not row:
        await callback_query.message.edit_text("❌ Срок действия фото истёк. Отправьте новое.")
        return
    file_id = row[0]

    now = datetime.now()
    shot_date = now.date() if choice == "today" else now.date() - timedelta(days=1)

    c.execute("SELECT 1 FROM photos WHERE user_id = ? AND shot_date = ?", (user_id, str(shot_date)))
    if c.fetchone():
        await callback_query.message.edit_text("⚠️ Вы уже отправляли фото за эту дату.")
        conn.execute("DELETE FROM temp_photos WHERE short_id = ?", (short_id,))
        conn.commit()
        conn.close()
        return

    c.execute("""
        INSERT INTO photos (user_id, username, file_id, shot_date, upvotes, downvotes)
        VALUES (?, ?, ?, ?, 0, 0)
    """, (user_id, username, file_id, str(shot_date)))
    conn.commit()

    # Сохраняем vote_id → file_id
    vote_id = str(uuid.uuid4())[:8]
    c.execute("INSERT OR REPLACE INTO vote_map (short_id, file_id) VALUES (?, ?)", (vote_id, file_id))
    conn.commit()

    c.execute("SELECT DISTINCT shot_date FROM photos WHERE user_id = ?", (user_id,))
    dates = sorted(datetime.strptime(row[0], "%Y-%m-%d").date() for row in c.fetchall())

    conn.execute("DELETE FROM temp_photos WHERE short_id = ?", (short_id,))
    conn.commit()
    conn.close()

    def current_streak(dates):
        streak = 0
        current = max(dates, default=None)
        while current and current in dates:
            streak += 1
            current -= timedelta(days=1)
        return streak

    def best_streak(dates):
        best = 0
        dates_set = set(dates)
        for d in dates:
            if (d - timedelta(days=1)) not in dates_set:
                length = 1
                current = d
                while (current + timedelta(days=1)) in dates_set:
                    length += 1
                    current += timedelta(days=1)
                best = max(best, length)
        return best

    day_number = (shot_date - CHALLENGE_START_DATE).days + 1
    caption = (
        f"🔥 День #{day_number} (#day{day_number})\n"
        f"📸 Автор: @{username} (#{username})\n"
        f"🗓 Дата съёмки: {shot_date}\n"
        f"📊 Серия: {current_streak(dates)} дней (рекорд: {best_streak(dates)})"
    )

    vote_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👍", callback_data=f"vote:{vote_id}:up"),
            InlineKeyboardButton(text="🤔", callback_data=f"vote:{vote_id}:down")
        ]
    ])

    await bot.send_photo(CHANNEL_ID, file_id, caption=caption, reply_markup=vote_keyboard)
    await callback_query.message.edit_text("✅ Фото опубликовано!")


@router.callback_query(F.data.startswith("vote:"))
async def handle_vote(callback_query: CallbackQuery):
    _, vote_id, direction = callback_query.data.split(":")
    user_id = callback_query.from_user.id

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    c.execute("SELECT file_id FROM vote_map WHERE short_id = ?", (vote_id,))
    row = c.fetchone()
    if not row:
        await callback_query.answer("⚠️ Голосование недоступно.")
        conn.close()
        return
    file_id = row[0]

    c.execute("SELECT 1 FROM votes WHERE voter_id = ? AND file_id = ?", (user_id, file_id))
    if c.fetchone():
        await callback_query.answer("⚠️ Вы уже голосовали.")
        conn.close()
        return

    c.execute("INSERT INTO votes (voter_id, file_id) VALUES (?, ?)", (user_id, file_id))
    if direction == "up":
        c.execute("UPDATE photos SET upvotes = upvotes + 1 WHERE file_id = ?", (file_id,))
    elif direction == "down":
        c.execute("UPDATE photos SET downvotes = downvotes + 1 WHERE file_id = ?", (file_id,))
    conn.commit()
    conn.close()

    await callback_query.answer("✅ Голос учтён.")


@router.callback_query(F.data.startswith("cancel:"))
async def cancel_photo(callback_query: CallbackQuery):
    short_id = callback_query.data.split(":")[1]
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("DELETE FROM temp_photos WHERE short_id = ?", (short_id,))
    conn.commit()
    conn.close()
    await callback_query.message.edit_text("❌ Загрузка отменена.")
