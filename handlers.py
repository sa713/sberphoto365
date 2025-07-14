from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart
from aiogram.enums import ContentType
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta
from config import CHAT_ID, CHANNEL_ID, TIMEZONE
import database
import sqlite3

router = Router()
photo_buffer = {}

@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет! Пришли мне фото для участия в челлендже 365.")

@router.message(F.chat.type == "private", F.content_type == ContentType.PHOTO)
async def handle_photo(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or f"id{user_id}"

    # Проверка участия
    if message.from_user.id != user_id:
        return

    # Проверка, состоит ли пользователь в нужном чате
    try:
        chat_member = await message.bot.get_chat_member(CHAT_ID, user_id)
        if chat_member.status not in ["member", "creator", "administrator"]:
            await message.answer("Ты не участник чата и не можешь участвовать в челлендже.")
            return
    except:
        await message.answer("Ошибка при проверке членства в чате.")
        return

    # Сохраняем фото во временное хранилище
    file_id = message.photo[-1].file_id
    photo_buffer[user_id] = {"file_id": file_id, "message": message}

    # Предложение выбора даты
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сегодня", callback_data="date_today")],
        [InlineKeyboardButton(text="Вчера", callback_data="date_yesterday")],
        [InlineKeyboardButton(text="Отменить", callback_data="cancel")]
    ])
    await message.answer("Выбери дату съёмки фотографии:", reply_markup=kb)

@router.callback_query(F.data.startswith("date_") | F.data == "cancel")
async def process_date_choice(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data
    await callback.message.delete()

    if data == "cancel":
        await callback.message.answer("Загрузка отменена.")
        photo_buffer.pop(user_id, None)
        return

    if user_id not in photo_buffer:
        await callback.message.answer("Нет фотографии для загрузки.")
        return

    shot_date = datetime.now(TIMEZONE).date()
    if data == "date_yesterday":
        shot_date -= timedelta(days=1)

    # Проверка повтора загрузки на сегодня
    today = datetime.now(TIMEZONE).date()
    conn = sqlite3.connect("photo_challenge.db")
    c = conn.cursor()
    c.execute("SELECT id FROM photos WHERE user_id = ? AND submission_date = ?", (user_id, str(today)))
    if c.fetchone():
        await callback.message.answer("Ты уже отправлял фото сегодня.")
        conn.close()
        return
    conn.close()

    file_id = photo_buffer[user_id]["file_id"]
    message = photo_buffer[user_id]["message"]
    username = message.from_user.username or f"id{user_id}"
    now = datetime.now(TIMEZONE)
    challenge_day = database.get_challenge_day(now.date())
    current_streak, max_streak = database.update_user_streak(user_id, username, shot_date)

    text = (
        f"<b>День {challenge_day} #day{challenge_day}</b>\n"
        f"Автор: @{username} #{username}\n"
        f"Дата съёмки: {shot_date.strftime('%Y-%m-%d')}\n"
        f"Серия: {current_streak} дней подряд\n"
        f"Рекорд: {max_streak} дней"
    )

    buttons = [
        [InlineKeyboardButton(text="👍", callback_data=f"vote_up"), InlineKeyboardButton(text="👎", callback_data=f"vote_down")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    sent = await message.bot.send_photo(CHANNEL_ID, file_id, caption=text, reply_markup=kb)
    active_until = now + timedelta(days=2)

    conn = sqlite3.connect("photo_challenge.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO photos (user_id, username, challenge_day, shot_date, submission_date, file_id, message_id, active_until)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, username, challenge_day, str(shot_date), str(now.date()), file_id, sent.message_id, str(active_until.date())))
    conn.commit()
    conn.close()

    await callback.message.answer("Фото опубликовано. Спасибо за участие!")
    photo_buffer.pop(user_id, None)

@router.callback_query(F.data.startswith("vote_"))
async def handle_vote(callback: CallbackQuery):
    vote_type = callback.data.split("_")[1]
    user_id = callback.from_user.id
    message_id = callback.message.message_id

    conn = sqlite3.connect("photo_challenge.db")
    c = conn.cursor()
    c.execute("SELECT id FROM photos WHERE message_id = ?", (message_id,))
    row = c.fetchone()
    if not row:
        await callback.answer("Фотография не найдена.")
        return

    photo_id = row[0]
    c.execute("SELECT vote FROM votes WHERE user_id = ? AND photo_id = ?", (user_id, photo_id))
    existing = c.fetchone()
    if existing:
        await callback.answer("Ты уже голосовал.")
        return

    c.execute("INSERT INTO votes (user_id, photo_id, vote) VALUES (?, ?, ?)", (user_id, photo_id, vote_type))
    if vote_type == "up":
        c.execute("UPDATE photos SET upvotes = upvotes + 1 WHERE id = ?", (photo_id,))
    else:
        c.execute("UPDATE photos SET downvotes = downvotes + 1 WHERE id = ?", (photo_id,))

    conn.commit()
    conn.close()

    await callback.answer("Голос учтён.")