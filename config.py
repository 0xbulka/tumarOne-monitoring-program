import os
from dotenv import load_dotenv

load_dotenv()

POLL_INTERVAL = 300  # 5 minutes
LANG = "EN"
TOKENS_FILE = "tokens.json"
MOCK_URL = "http://localhost:4000"

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set. Please set it for your bot.")
TUMAR_API_URL = os.getenv("TUMAR_API_URL")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
TUMAR_AUTH_CODE = os.getenv("TUMAR_AUTH_CODE")
KNOWN_IDS_FILE = os.getenv("KNOWN_IDS_FILE")