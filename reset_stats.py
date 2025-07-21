# v1.0

import sqlite3
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

cursor.execute("DELETE FROM photos;")
conn.commit()

print("📸 Таблица 'photos' очищена.")
conn.close()
