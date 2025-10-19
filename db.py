import sqlite3
from pathlib import Path

DB_PATH = Path("books.db")

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
