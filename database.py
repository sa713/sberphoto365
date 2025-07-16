import sqlite3
from config import DATABASE_PATH

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    # Таблица с основными фото
    c.execute("""
    CREATE TABLE IF NOT EXISTS photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        file_id TEXT NOT NULL,
        shot_date TEXT NOT NULL,
        upvotes INTEGER DEFAULT 0,
        downvotes INTEGER DEFAULT 0
    )
    """)

    # Индексы для ускорения выборок по голосованию и дате
    c.execute("CREATE INDEX IF NOT EXISTS idx_photos_user_date ON photos(user_id, shot_date)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_photos_file_id ON photos(file_id)")

    # Таблица голосов
    c.execute("""
    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voter_id INTEGER NOT NULL,
        file_id TEXT NOT NULL
    )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_votes_voter_file ON votes(voter_id, file_id)")

    conn.commit()
    conn.close()
