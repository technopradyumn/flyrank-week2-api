# AI-generated implementation of Containerized PostgreSQL Task API
import os
import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL", "postgres://postgres:dev@db:5432/tasks")

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

@app.on_event("startup")
def startup():
    conn = psycopg.connect(DATABASE_URL)
    with conn.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS tasks (id SERIAL PRIMARY KEY, title TEXT, done BOOLEAN DEFAULT FALSE);")
        cur.execute("INSERT INTO tasks (title, done) VALUES ('Task 1', false), ('Task 2', false), ('Task 3', true);")
    conn.commit()
    conn.close()
