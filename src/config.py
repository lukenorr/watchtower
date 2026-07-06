"""Single source of truth for env vars and config"""
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set in environment or .env file")

URLHAUS_API_KEY = os.environ.get("URLHAUS_API_KEY")

if not URLHAUS_API_KEY:
    raise ValueError("URLHAUS_API_KEY not set in environment or .env file")

NTFY_TOPIC = os.environ.get("NTFY_TOPIC")

if not NTFY_TOPIC:
    raise ValueError("NTFY_TOPIC not set in environment or .env file")