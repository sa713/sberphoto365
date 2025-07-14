import sqlite3
from datetime import datetime, date, timedelta

DB_PATH = "photo_challenge.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        current_streak INTEGER DEFAULT 0,
        max_streak INTEGER DEFAULT 0,
        last_submission_date TEXT
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        challenge_day INTEGER,
        shot_date TEXT,
        submission_date TEXT,
        file_id TEXT,
        upvotes INTEGER DEFAULT 0,
        downvotes INTEGER DEFAULT 0,
        message_id INTEGER,
        active_until TEXT
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS votes (
        user_id INTEGER,
        photo_id INTEGER,
        vote TEXT CHECK(vote IN ('up', 'down')),
        PRIMARY KEY (user_id, photo_id)
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS meta (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')

    c.execute("INSERT OR IGNORE INTO meta (key, value) VALUES ('start_date', ?)", (str(date.today()),))

    conn.commit()
    conn.close()

def get_challenge_day(submission_date: date) -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM meta WHERE key = 'start_date'")
    row = c.fetchone()
    start_date = date.fromisoformat(row[0]) if row else submission_date
    delta = (submission_date - start_date).days + 1
    return delta

def update_user_streak(user_id: int, username: str, shot_date: date):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    today = date.today()
    c.execute("SELECT current_streak, max_streak, last_submission_date FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if row:
        current_streak, max_streak, last_date_str = row
        last_date = date.fromisoformat(last_date_str) if last_date_str else None

        if last_date == today - timedelta(days=1):
            current_streak += 1
        else:
            current_streak = 1

        max_streak = max(max_streak, current_streak)

        c.execute("""
            UPDATE users
            SET username = ?, current_streak = ?, max_streak = ?, last_submission_date = ?
            WHERE user_id = ?
        """, (username, current_streak, max_streak, str(today), user_id))
    else:
        current_streak = 1
        max_streak = 1
        c.execute("""
            INSERT INTO users (user_id, username, current_streak, max_streak, last_submission_date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, current_streak, max_streak, str(today)))

    conn.commit()
    conn.close()
    return current_streak, max_streak