from dotenv import load_dotenv
import os

load_dotenv()

DB_BACKEND = os.getenv("DB_BACKEND", "sqlite")
SQLITE_PATH = os.getenv("SQLITE_PATH", "tasks.db")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://taskuser:taskpass@localhost:5432/tasks")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "google/gemini-2.5-flash-lite")

LLM_STUB = os.getenv("LLM_STUB", "0") == "1"
LLM_ENABLED = os.getenv("LLM_ENABLED", "true").lower() != "false"

LLM_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
LLM_MAX_ATTEMPTS = int(os.getenv("LLM_MAX_ATTEMPTS", "3"))

PROMPT_VERSION = os.getenv("PROMPT_VERSION", "triage-v1")
QUARANTINE_PATH = os.getenv("QUARANTINE_PATH", "logs/quarantine.jsonl")
