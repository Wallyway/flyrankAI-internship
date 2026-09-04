from dotenv import load_dotenv
import os

load_dotenv()

DB_BACKEND = os.getenv("DB_BACKEND", "sqlite")
SQLITE_PATH = os.getenv("SQLITE_PATH", "tasks.db")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://taskuser:taskpass@localhost:5432/tasks")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
