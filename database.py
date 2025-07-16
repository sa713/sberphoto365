import sqlite3
from config import DATABASE_PATH

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    # Таблица для фотографий
    c.execute("""
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            file_id TEXT NOT NULL,
            shot_date TEXT NOT NULL,
            upvotes INTEGER DEFAULT 0,
            downvotes INTEGER DEFAULT 0
        )
    """)

    # Таблица для голосов
    c.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id INTEGER NOT NULL,
            file_id TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
