from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db():
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT FALSE
        )
    """)
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()["count"]
    if count == 0:
        conn.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s), (%s, %s), (%s, %s)",
            ("Buy milk", False, "Walk the dog", False, "Finish assignment", True)
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
    return rows


@app.get("/tasks/{tasks_id}")
def get_task(tasks_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM tasks WHERE id = %s", (tasks_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {tasks_id} not found")
    return row


@app.post("/tasks", status_code=201)
def create_task(new_task: TaskCreate):
    if not new_task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")

    conn = get_db()
    row = conn.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *",
        (new_task.title, False)
    ).fetchone()
    conn.commit()
    conn.close()
    return row


@app.put("/tasks/{tasks_id}")
def update_task(tasks_id: int, updated: TaskUpdate):
    conn = get_db()
    row = conn.execute("SELECT * FROM tasks WHERE id = %s", (tasks_id,)).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {tasks_id} not found")

    new_title = row["title"]
    new_done = row["done"]

    if updated.title is not None:
        if not updated.title.strip():
            conn.close()
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        new_title = updated.title
    if updated.done is not None:
        new_done = updated.done

    updated_row = conn.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *",
        (new_title, new_done, tasks_id)
    ).fetchone()
    conn.commit()
    conn.close()
    return updated_row


@app.delete("/tasks/{tasks_id}", status_code=204)
def delete_task(tasks_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM tasks WHERE id = %s", (tasks_id,)).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {tasks_id} not found")
    conn.execute("DELETE FROM tasks WHERE id = %s", (tasks_id,))
    conn.commit()
    conn.close()