SEED_TASKS = [
    {"id": 1, "title": "Learn HTTP and REST basics", "done": True},
    {"id": 2, "title": "Build CRUD endpoints", "done": False},
    {"id": 3, "title": "Test with Swagger UI", "done": False},
]

tasks: list[dict] = [t.copy() for t in SEED_TASKS]
next_id: int = 4
