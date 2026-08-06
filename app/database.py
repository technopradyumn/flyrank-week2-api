import os
import time
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgres://postgres:dev@localhost:5432/tasks")

SEED_TASKS = [
    {"title": "Learn HTTP and REST basics", "done": True},
    {"title": "Build CRUD endpoints", "done": False},
    {"title": "Test with Swagger UI", "done": False},
]

def get_db():
    retries = 10
    while retries > 0:
        try:
            conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
            return conn
        except psycopg.OperationalError:
            retries -= 1
            if retries == 0:
                raise
            time.sleep(1)

def init_db():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_title ON tasks(title);")
        
        cursor.execute("SELECT COUNT(*) FROM tasks;")
        count = cursor.fetchone()["count"]
        
        if count == 0:
            for task in SEED_TASKS:
                cursor.execute(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s);",
                    (task["title"], task["done"]),
                )
    conn.commit()
    conn.close()

def reset_db():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE tasks RESTART IDENTITY;")
        for task in SEED_TASKS:
            cursor.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s);",
                (task["title"], task["done"]),
            )
    conn.commit()
    conn.close()

# Initialize DB on module import
init_db()
