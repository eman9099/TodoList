from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import sqlite3

def get_db():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
    """)
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [("Buy milk", 0), ("Walk the dog", 0), ("Finish assignment", 1)]
        )
    conn.commit()
    conn.close()

init_db()

app = FastAPI()

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    conn = get_db()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/tasks/{tasks_id}")
def get_task(tasks_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (tasks_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {tasks_id} not found")
    return dict(row)

@app.post("/tasks", status_code=201)
def create_task(new_task: TaskCreate):
    if not new_task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")

    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (new_task.title, 0)
    )
    conn.commit()
    new_id = cursor.lastrowid
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (new_id,)).fetchone()
    conn.close()
    return dict(row)

# NOTE: PUT and DELETE below still use the old in-memory list.
# We will replace these in Stage 3 to use the database too.
tasks = []

@app.put("/tasks/{tasks_id}")
def update_task(tasks_id: int, updated: TaskUpdate):
    for task in tasks:
        if task["id"] == tasks_id:
            if updated.title is not None:
                if not updated.title.strip():
                    raise HTTPException(status_code=400, detail="Title cannot be empty")
                task["title"] = updated.title
            if updated.done is not None:
                task["done"] = updated.done
            return task
    raise HTTPException(status_code=404, detail=f"Task {tasks_id} not found")

@app.delete("/tasks/{tasks_id}", status_code=204)
def delete_task(tasks_id: int):
    for task in tasks:
        if task["id"] == tasks_id:
            tasks.remove(task)
            return
    raise HTTPException(status_code=404, detail=f"Task {tasks_id} not found")