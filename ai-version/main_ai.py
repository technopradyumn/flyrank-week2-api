# AI-generated version — Stage 7 rematch
# Generated from prompt in prompt.txt (second iteration, after refining the prompt).
# Compare with ../main.py using:  git diff --no-index main.py ai-version/main_ai.py

from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Task API (AI version)", version="1.0")

# In-memory task list
tasks: list[dict] = [
    {"id": 1, "title": "Read the FastAPI docs", "done": True},
    {"id": 2, "title": "Write my first endpoint", "done": False},
    {"id": 3, "title": "Deploy to production", "done": False},
]
_next_id = 4


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.get("/tasks")
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
    return task


@app.post("/tasks", status_code=201)
def create_task(body: TaskCreate):
    global _next_id
    if not body.title or not body.title.strip():
        return JSONResponse(status_code=400, content={"error": "title is required and cannot be empty"})
    new_task = {"id": _next_id, "title": body.title.strip(), "done": False}
    tasks.append(new_task)
    _next_id += 1
    return JSONResponse(status_code=201, content=new_task)


@app.put("/tasks/{task_id}")
def update_task(task_id: int, body: TaskUpdate):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
    if body.title is None and body.done is None:
        return JSONResponse(status_code=400, content={"error": "Body must include at least one of: title, done"})
    if body.title is not None:
        if not body.title.strip():
            return JSONResponse(status_code=400, content={"error": "title cannot be empty"})
        task["title"] = body.title.strip()
    if body.done is not None:
        task["done"] = body.done
    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global tasks
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
    tasks = [t for t in tasks if t["id"] != task_id]
    return Response(status_code=204)  # AI used Response() instead of JSONResponse(204, content=None)
