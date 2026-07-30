from fastapi import FastAPI, HTTPException

tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Walk the dog", "done": False},
    {"id": 3, "title": "Finish assignment", "done": True},
]
app = FastAPI()
@app.get("/")
def read_root():
    return{
        "name": "Task API",
        "version": "1.0",
        "endpoints":["/tasks"]
           }
@app.get("/health")
def health_check():
    return{"status":"ok"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{tasks_id}")
def get_tasks(tasks_id:int):
    for task in tasks:
        if task["id"]==tasks_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {tasks_id} not found")

