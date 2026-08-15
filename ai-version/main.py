from contextlib import asynccontextmanager
import sqlite3
from typing import Optional
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

DATABASE = "ai_tasks.db"


def init_db():
  with sqlite3.connect(DATABASE) as conn:
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
        """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
      sample_tasks = [
          ("Buy groceries", 0),
          ("Read FastAPI documentation", 1),
          ("Build a todo app with SQLite", 0),
      ]
      cursor.executemany(
          "INSERT INTO tasks (title, done) VALUES (?, ?)", sample_tasks
      )
    conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
  init_db()
  yield


app = FastAPI(lifespan=lifespan)


class TaskCreate(BaseModel):
  title: str
  done: bool = False


class TaskUpdate(BaseModel):
  title: Optional[str] = None
  done: Optional[bool] = None


@app.get("/tasks")
def get_tasks():
  with sqlite3.connect(DATABASE) as conn:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    return [
        {"id": r["id"], "title": r["title"], "done": bool(r["done"])}
        for r in rows
    ]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
  with sqlite3.connect(DATABASE) as conn:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
    )
    row = cursor.fetchone()
    if not row:
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
      )
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
  if not task.title or not task.title.strip():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Title cannot be missing or empty",
    )

  with sqlite3.connect(DATABASE) as conn:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title.strip(), 1 if task.done else 0),
    )
    conn.commit()
    new_id = cursor.lastrowid

    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
  if task.title is not None and not task.title.strip():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Title cannot be empty"
    )

  with sqlite3.connect(DATABASE) as conn:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
    )
    existing = cursor.fetchone()
    if not existing:
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
      )

    new_title = (
        task.title.strip() if task.title is not None else existing["title"]
    )
    new_done = (
        (1 if task.done else 0) if task.done is not None else existing["done"]
    )

    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, task_id),
    )
    conn.commit()

    return {"id": task_id, "title": new_title, "done": bool(new_done)}


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
  with sqlite3.connect(DATABASE) as conn:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    if cursor.rowcount == 0:
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
      )
    return Response(status_code=status.HTTP_204_NO_CONTENT)