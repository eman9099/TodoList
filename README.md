# Task API

A small CRUD API built with **Python + FastAPI** that manages a to-do list. Data is stored in memory (no database) — it resets whenever the server restarts.

Built as part of the FlyRank Internship — Backend Track, Week 2, Assignment A1.

## How to run it

1. Clone this repo and go into the folder:
   ```bash
   git clone https://github.com/eman9099/TodoList.git
   cd TodoList
   ```

2. (Optional but recommended) create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```

3. Install the dependencies:
   ```bash
   pip install fastapi uvicorn
   ```

4. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

5. Open your browser:
   - API root: http://127.0.0.1:8000/
   - Interactive docs (Swagger UI): http://127.0.0.1:8000/docs

## Endpoints

| Method | Path              | Description                        |
|--------|-------------------|-------------------------------------|
| GET    | `/`                | API info                           |
| GET    | `/health`          | Health check                       |
| GET    | `/tasks`           | List all tasks                     |
| GET    | `/tasks/{task_id}` | Get a single task by id            |
| POST   | `/tasks`           | Create a new task                  |
| PUT    | `/tasks/{task_id}` | Update a task's title and/or done  |
| DELETE | `/tasks/{task_id}` | Delete a task                      |

Each task has this shape:
```json
{ "id": 1, "title": "Buy milk", "done": false }
```

## Status codes

- `200` — successful read/update
- `201` — task created
- `204` — task deleted (no content returned)
- `400` — invalid input (e.g. missing/empty title)
- `404` — task not found

## Example: curl

Creating a task:
```bash
curl -i -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Buy milk\"}"
```

Response:
```
HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Swagger UI

The full CRUD cycle (create, read, update, delete) was tested using the interactive **Try it out** feature at `/docs`.

![Swagger UI - all endpoints](screenshots/s1.png)
![Swagger UI - GET /tasks/{id}](screenshots/s2.png)
![Swagger UI - PUT /tasks/{id}](screenshots/s3.png)
![Swagger UI - POST /tasks](screenshots/s4.png)
![Swagger UI - DELETE /tasks/{id}](screenshots/s5.png)

## Notes on in-memory storage

Since tasks are stored in a plain Python list (not a database), restarting the server resets the list back to the 3 example tasks. This is expected — persistent storage is covered in a later assignment.

## Bonus Stage 7 — AI vs me

I wrote my own spec from memory (without looking back at the assignment doc) and asked an AI assistant to build the same API. The AI's code lives in `ai-version/` and was never mixed with my hand-built code.

### My prompt

> Build a to-do list REST API using Python and FastAPI. Data should be stored in memory (a Python list) — no database.
>
> Each task should have: `id` (integer), `title` (string), `done` (boolean, defaults to false).
>
> Endpoints needed:
> - `GET /tasks` — return all tasks
> - `GET /tasks/{id}` — return a single task; if not found, return 404 with a JSON error message
> - `POST /tasks` — create a new task from a `title` in the request body; return 201 with the created task; if title is missing or empty, return 400 with an error message
> - `PUT /tasks/{id}` — update a task's title and/or done status; return 404 if the id doesn't exist
> - `DELETE /tasks/{id}` — delete a task; return 204 with no body; return 404 if the id doesn't exist
>
> Also add `GET /` returning basic API info, and `GET /health` returning a status check.
>
> Automatically generate interactive Swagger UI documentation at `/docs`.

### Running it

I fired my Stage 4 checkpoint curls at the AI's version (running on port 8001) and every one passed: `GET /tasks`, `POST /tasks` (201), `GET /tasks/{id}` (200), `PUT /tasks/{id}` (200), `DELETE /tasks/{id}` (204), and validation on an empty title (400).

### What did the AI do better?

It used `response_model=Task` on every endpoint, so FastAPI validates the *response* shape too, not just the request. It also used readable constants like `status.HTTP_201_CREATED` instead of hardcoded numbers like `201` — makes the code easier to read at a glance. I understand both changes well enough to explain them, and I've started using `status.HTTP_xxx` in my own code too.

### What did it get wrong or quietly ignore?

Nothing was actually wrong — all my required behaviors were followed correctly. But it made a couple of silent decisions I didn't specify (see below).

### What did my prompt forget to specify — and what did the AI decide for me?

- I never said the list should start with example data, so the AI's version starts completely empty (`tasks_db = []`), while my version starts with 3 pre-filled tasks.
- I didn't specify the path parameter's name, so the AI used `id` while I had used `tasks_id`.
- I didn't specify how new ids should be generated, so the AI used a separate global counter (`current_id`) instead of computing `max(existing ids) + 1` like I did.

### One rematch

For the second attempt, I added to my prompt: *"Pre-fill the in-memory list with 3 example tasks on startup."* The regenerated version then started with 3 tasks instead of an empty list, matching my original API's behavior.
