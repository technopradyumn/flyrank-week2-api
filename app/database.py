import sqlite3
import os

DB_FILE = os.getenv("TASKS_DB", "tasks.db")

SEED_TASKS = [
    {"title": "Learn HTTP and REST basics", "done": True},
    {"title": "Build CRUD endpoints", "done": False},
    {"title": "Test with Swagger UI", "done": False},
]

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_title ON tasks(title);")
    
    cursor.execute("SELECT COUNT(*) FROM tasks;")
    count = cursor.fetchone()[0]
    
    if count == 0:
        with conn:
            for task in SEED_TASKS:
                conn.execute(
                    "INSERT INTO tasks (title, done) VALUES (?, ?);",
                    (task["title"], 1 if task["done"] else 0),
                )
    conn.close()

def reset_db():
    conn = get_db()
    with conn:
        conn.execute("DELETE FROM tasks;")
        conn.execute("DELETE FROM sqlite_sequence WHERE name='tasks';")
        for task in SEED_TASKS:
            conn.execute(
                "INSERT INTO tasks (title, done) VALUES (?, ?);",
                (task["title"], 1 if task["done"] else 0),
            )
    conn.close()

# Initialize DB on module import
init_db()
