from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
app = FastAPI(
    title="To-Do List API",
    description="In-memory REST API built with FastAPI",
    version="1.0.0"
)
# In-memory storage and ID counter
tasks_db: List[dict] = []
current_id: int = 1
# --- Pydantic Models ---
class Task(BaseModel):
    id: int
    title: str
    done: bool = False
class TaskCreate(BaseModel):
    title: Optional[str] = None
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None
# --- General Endpoints ---
@app.get("/")
def get_api_info():
    return {
        "name": "To-Do List API",
        "version": "1.0.0",
        "description": "A lightweight in-memory To-Do REST API",
        "docs_url": "/docs"
    }
@app.get("/health")
def health_check():
    return {"status": "ok"}
# --- Task Resource Endpoints ---
@app.get("/tasks", response_model=List[Task])
def get_tasks():
    return tasks_db
@app.get("/tasks/{id}", response_model=Task)
def get_task(id: int):
    task = next((t for t in tasks_db if t["id"] == id), None)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {id} not found"
        )
    return task
@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    global current_id
    
    if not payload.title or not payload.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required and cannot be empty"
        )
    new_task = {
        "id": current_id,
        "title": payload.title.strip(),
        "done": False
    }
    tasks_db.append(new_task)
    current_id += 1
    return new_task
@app.put("/tasks/{id}", response_model=Task)
def update_task(id: int, payload: TaskUpdate):
    task = next((t for t in tasks_db if t["id"] == id), None)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {id} not found"
        )
    if payload.title is not None:
        if not payload.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title cannot be empty"
            )
        task["title"] = payload.title.strip()
    if payload.done is not None:
        task["done"] = payload.done
    return task
@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int):
    global tasks_db
    for index, task in enumerate(tasks_db):
        if task["id"] == id:
            tasks_db.pop(index)
            return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with ID {id} not found"
    )