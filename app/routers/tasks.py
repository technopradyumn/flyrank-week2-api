from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response

import app.database as db
from app.models import TaskCreate, TaskUpdate

router = APIRouter(tags=["tasks"])


def task_row_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


@router.get("/tasks", summary="List all tasks")
def get_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    conn = db.get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []
    
    if done is not None:
        query += " AND done = ?"
        params.append(1 if done else 0)
    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")
        
    query += " ORDER BY id ASC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [task_row_to_dict(row) for row in rows]


@router.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?;", (task_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
    return task_row_to_dict(row)


@router.post("/tasks", status_code=201, summary="Create a task")
def create_task(body: TaskCreate):
    if not body.title or not body.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "title is required and cannot be empty"},
        )
    
    title = body.title.strip()
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, 0);", (title,))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    new_task = {"id": new_id, "title": title, "done": False}
    return JSONResponse(status_code=201, content=new_task)


@router.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, body: TaskUpdate):
    conn = db.get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tasks WHERE id = ?;", (task_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
        
    if body.title is None and body.done is None:
        conn.close()
        return JSONResponse(
            status_code=400,
            content={"error": "Body must include at least one of: title, done"},
        )
        
    current_title = existing["title"]
    current_done = bool(existing["done"])
    
    if body.title is not None:
        if not body.title.strip():
            conn.close()
            return JSONResponse(status_code=400, content={"error": "title cannot be empty"})
        current_title = body.title.strip()
        
    if body.done is not None:
        current_done = body.done
        
    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?;",
        (current_title, 1 if current_done else 0, task_id),
    )
    conn.commit()
    conn.close()
    
    return {"id": task_id, "title": current_title, "done": current_done}


@router.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks WHERE id = ?;", (task_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
        
    cursor.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
    conn.commit()
    conn.close()
    return Response(status_code=204)


@router.get("/stats", tags=["extras"], summary="Task statistics")
def get_stats():
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks;")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = 1;")
    done = cursor.fetchone()[0]
    conn.close()
    
    return {"total": total, "done": done, "open": total - done}


@router.post("/reset", tags=["extras"], summary="Reset to seed data")
def reset_tasks():
    db.reset_db()
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY id ASC;")
    rows = cursor.fetchall()
    conn.close()
    tasks_list = [task_row_to_dict(r) for r in rows]
    return {"message": "Tasks reset to seed data", "tasks": tasks_list}
