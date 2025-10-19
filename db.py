import os
import sqlite3
from pathlib import Path

# Use Render disk if provided, else local folder
DATA_DIR = Path(os.environ.get("DATA_DIR", "."))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "books.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    sql = Path("schema.sql").read_text(encoding="utf-8")
    with get_conn() as conn:
        conn.executescript(sql)

if __name__ == "__main__":
    init_db()
    print("DB ready at", DB_PATH.resolve())
