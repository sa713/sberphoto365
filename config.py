import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
CHAT_ID = int(os.getenv("CHAT_ID"))

# Путь к базе данных
DATABASE_PATH = "photo_challenge.db"

# Дата начала челленджа (день №1)
#CHALLENGE_START_DATE = datetime.strptime(os.getenv("CHALLENGE_START_DATE"), "%Y-%m-%d").date()
CHALLENGE_START_DATE = date(2025, 7, 16)

# Время публикации сводки (по МСК)
PUBLISH_HOUR = int(os.getenv("PUBLISH_HOUR", 8))  # час (0–23)
PUBLISH_MINUTE = int(os.getenv("PUBLISH_MINUTE", 0))  # минута (0–59)

# Путь к лог-файлу
LOG_FILE_PATH = "bot.log"
