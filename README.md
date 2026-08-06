# Task API — FlyRank Internship · Backend Track · Week 1 · Assignment A3

A persistent, containerized **CRUD REST API** for managing to-do tasks, built with **Python (FastAPI) + PostgreSQL + Docker + Docker Compose**.

Data lives in a real **PostgreSQL database server (`taskdb`)** inside a Docker container, with a named Docker volume (`taskdata`) ensuring full persistence across restarts.

---

## Quick Start (One Command)

```bash
# 1. Clone the repo and enter the directory
git clone https://github.com/technopradyumn/flyrank-week2-api
cd API

# 2. Copy the environment variables template
cp .env.example .env

# 3. Start the entire stack (API + PostgreSQL DB) with ONE command
docker compose up
```

The app will start at **http://localhost:3000**  
Interactive Swagger docs: **http://localhost:3000/docs**

---

## Environment Variables & Configuration

Configuration is managed via `.env` (git-ignored for security). A committed `.env.example` serves as the template:

```env
DATABASE_URL=postgres://postgres:dev@localhost:5432/tasks
```

Inside the Docker Compose network, the API service automatically connects to the PostgreSQL container using the service name:
`postgres://postgres:dev@db:5432/tasks`

---

## Endpoints

| Method   | Path          | Status (success) | Description                              |
|----------|---------------|------------------|------------------------------------------|
| `GET`    | `/`           | 200              | API name, version, and endpoints list    |
| `GET`    | `/health`     | 200              | Liveness probe — `{"status":"ok"}`       |
| `GET`    | `/tasks`      | 200              | List all tasks (supports `done`/`search`)|
| `GET`    | `/tasks/{id}` | 200 / 404        | Get one task by ID                       |
| `POST`   | `/tasks`      | 201 / 400        | Create a new task (`RETURNING *`)        |
| `PUT`    | `/tasks/{id}` | 200 / 400 / 404  | Update title and/or done status          |
| `DELETE` | `/tasks/{id}` | 204 / 404        | Delete a task                            |
| `GET`    | `/stats`      | 200              | ★ Task statistics (total, done, open)    |
| `POST`   | `/reset`      | 200              | ★ Reset database to 3 seed tasks         |

---

## Verification via `curl -i`

```bash
curl -i http://localhost:3000/tasks
```

**Output:**
```http
HTTP/1.1 200 OK
date: Thu, 06 Aug 2026 04:47:32 GMT
server: uvicorn
content-length: 195
content-type: application/json

[
  {"id":1,"title":"Learn HTTP and REST basics","done":true},
  {"id":2,"title":"Build CRUD endpoints","done":false},
  {"id":3,"title":"Test with Swagger UI","done":false}
]
```

---

## Database Screenshot & Inspection

You can inspect the running PostgreSQL database inside the container using `psql`:

```bash
docker compose exec db psql -U postgres -d tasks -c "\dt"
```

**Output:**
```text
         List of relations
 Schema | Name  | Type  |  Owner   
--------+-------+-------+----------
 public | tasks | table | postgres
(1 row)
```

```bash
docker compose exec db psql -U postgres -d tasks -c "SELECT * FROM tasks;"
```

**Output:**
```text
 id |           title            | done 
----+----------------------------+------
  1 | Learn HTTP and REST basics | t
  2 | Build CRUD endpoints       | f
  3 | Test with Swagger UI       | f
  5 | Persistent Container Task  | f
(4 rows)
```

---

## Persistence Proof

Data persistence across a full stack restart is guaranteed by the `taskdata` Docker volume:
1. Create a task via API.
2. Stop and remove containers: `docker compose down`.
3. Bring stack back up: `docker compose up -d`.
4. Querying `GET /tasks` proves all tasks persist because the volume outlives container lifecycle.

---

## Why Identical Tests Passing Proves Storage Abstraction

The test suite in `test_main.py` runs identical API tests across:
1. In-Memory (Assignment A1)
2. SQLite File (Assignment A2)
3. Containerized PostgreSQL (Assignment A3)

Because the API routes, status codes, and JSON schemas remain identical across all 3 storage swaps, this proves that **storage is merely an implementation detail** isolated behind our database module (`app/database.py`).

---

## AI vs Me — Stage 6 Rematch

### Prompt Used (from memory):
> "Containerize a FastAPI Python task CRUD API with a PostgreSQL database using Docker and Docker Compose. Use psycopg v3 driver, load connection string from .env (DATABASE_URL), create the tasks table (id SERIAL PRIMARY KEY, title TEXT, done BOOLEAN) if not existing, seed 3 example tasks only when empty. Use parameterized queries (%s). Write Dockerfile and compose.yaml with api and db services and named volume taskdata for data persistence. One command docker compose up must start the full stack."

### 3 Concrete Differences Found:

1. **Database Service Readiness / Retry Handling**:
   - *Manual*: Implemented retry logic in `app/database.py` (`get_db()`) to gracefully retry connections when starting alongside the PostgreSQL container.
   - *AI*: Used `depends_on: [db]` without a healthcheck or connection retry loop in Python, causing the API container to crash if PostgreSQL took >2 seconds to initialize first time.

2. **Secrets & Environment Injection**:
   - *Manual*: Maintained clean separation using `.env` (git-ignored) and `.env.example` (committed), pointing compose to `db:5432` internally while local dev uses `localhost:5432`.
   - *AI*: Hardcoded `POSTGRES_PASSWORD=dev` directly inside `app/database.py` as fallback default string instead of reading strictly from environment variables.

3. **Docker Image Optimization**:
   - *Manual*: Selected lightweight `python:3.12-slim` and `postgres:15-alpine` images, resulting in minimal image footprint and fast startup times.
   - *AI*: Used standard `python:3.12` (over 1 GB base image) and `postgres:latest` without specifying multi-stage or slim variants.

### One-Sentence Rematch Result:
Adding explicit retry handling for database connection readiness and specifying `python:3.12-slim` in the prompt eliminated initial container crashes and reduced the resulting image footprint significantly.

---

## Project Structure

```
API/
├── Dockerfile           # Multi-stage/slim Docker image recipe for FastAPI app
├── compose.yaml         # Docker Compose configuration (api + db services)
├── .env.example         # Template environment secrets
├── .gitignore           # Ignores .env and virtual environments
├── requirements.txt     # Dependencies (fastapi, uvicorn, psycopg, python-dotenv)
├── README.md            # Comprehensive documentation
├── test_main.py         # Test suite passing against PostgreSQL
├── app/
│   ├── main.py          # FastAPI application entrypoint
│   ├── database.py      # PostgreSQL connection, retry loop, seed logic
│   ├── models.py        # Pydantic schemas
│   └── routers/
│       ├── meta.py      # Health & metadata endpoints
│       └── tasks.py     # Parameterized PostgreSQL CRUD endpoints
└── ai-version/
    ├── prompt.txt       # AI prompt for Stage 6
    └── main_ai.py       # AI-generated implementation comparison
```
