# v1.0

from database import init_db
import sqlite3
from config import DATABASE_PATH

def init_temp_photos():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    # Временное хранилище фото
    c.execute("""
    CREATE TABLE IF NOT EXISTS temp_photos (
        short_id TEXT PRIMARY KEY,
        file_id TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Таблица для отображения vote_id → file_id
    c.execute("""
    CREATE TABLE IF NOT EXISTS vote_map (
        short_id TEXT PRIMARY KEY,
        file_id TEXT NOT NULL
    )
    """)

    # Индексы и автоматическая очистка старых записей
    c.execute("CREATE INDEX IF NOT EXISTS idx_temp_photos_created_at ON temp_photos(created_at)")
    c.execute("""
    DELETE FROM temp_photos
    WHERE created_at < datetime('now', '-10 minutes')
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    init_temp_photos()
    print("✅ База данных успешно создана и готова к работе.")
