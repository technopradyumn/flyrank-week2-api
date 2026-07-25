from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response

import app.database as db
from app.models import TaskCreate, TaskUpdate

router = APIRouter(tags=["tasks"])


@router.get("/tasks", summary="List all tasks")
def get_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    result = db.tasks
    if done is not None:
        result = [t for t in result if t["done"] == done]
    if search:
        result = [t for t in result if search.lower() in t["title"].lower()]
    return result


@router.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    task = next((t for t in db.tasks if t["id"] == task_id), None)
    if not task:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
    return task


@router.post("/tasks", status_code=201, summary="Create a task")
def create_task(body: TaskCreate):
    if not body.title or not body.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "title is required and cannot be empty"},
        )
    new_task = {"id": db.next_id, "title": body.title.strip(), "done": False}
    db.tasks.append(new_task)
    db.next_id += 1
    return JSONResponse(status_code=201, content=new_task)


@router.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, body: TaskUpdate):
    task = next((t for t in db.tasks if t["id"] == task_id), None)
    if not task:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
    if body.title is None and body.done is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Body must include at least one of: title, done"},
        )
    if body.title is not None:
        if not body.title.strip():
            return JSONResponse(status_code=400, content={"error": "title cannot be empty"})
        task["title"] = body.title.strip()
    if body.done is not None:
        task["done"] = body.done
    return task


@router.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    task = next((t for t in db.tasks if t["id"] == task_id), None)
    if not task:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
    db.tasks[:] = [t for t in db.tasks if t["id"] != task_id]
    return Response(status_code=204)


@router.get("/stats", tags=["extras"], summary="Task statistics")
def get_stats():
    total = len(db.tasks)
    done = sum(1 for t in db.tasks if t["done"])
    return {"total": total, "done": done, "open": total - done}


@router.post("/reset", tags=["extras"], summary="Reset to seed data")
def reset_tasks():
    db.tasks[:] = [t.copy() for t in db.SEED_TASKS]
    db.next_id = 4
    return {"message": "Tasks reset to seed data", "tasks": db.tasks}
