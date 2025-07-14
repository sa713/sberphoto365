import os
from datetime import timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # ID канала для публикаций
CHAT_ID = int(os.getenv("CHAT_ID"))        # ID чата с участниками

TIMEZONE = timezone(timedelta(hours=3))  # МСК
PUBLISH_HOUR = 1                          # 01:00 МСК
DATABASE_PATH = "photo_challenge.db"