import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.database import reset_db, get_db

client = TestClient(app)

class TestTaskAPI(unittest.TestCase):
    def setUp(self):
        reset_db()

    def test_root(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.json())

    def test_health(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_get_tasks(self):
        response = client.get("/tasks")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

    def test_get_task_by_id(self):
        response = client.get("/tasks/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], 1)

    def test_get_task_not_found(self):
        response = client.get("/tasks/999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "Task 999 not found"})

    def test_create_task(self):
        response = client.post("/tasks", json={"title": "Test task"})
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["title"], "Test task")
        self.assertFalse(data["done"])
        self.assertEqual(data["id"], 4)

    def test_create_task_empty_title(self):
        response = client.post("/tasks", json={"title": ""})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "title is required and cannot be empty"})

    def test_update_task(self):
        response = client.put("/tasks/1", json={"title": "Updated Title", "done": False})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Updated Title")

    def test_delete_task(self):
        response = client.delete("/tasks/1")
        self.assertEqual(response.status_code, 204)
        get_res = client.get("/tasks/1")
        self.assertEqual(get_res.status_code, 404)

    def test_stats(self):
        response = client.get("/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total", data)
        self.assertIn("done", data)
        self.assertIn("open", data)

    def test_reset(self):
        client.post("/tasks", json={"title": "Temporary Task"})
        response = client.post("/reset")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(client.get("/tasks").json()), 3)

    def test_persistence_across_restart(self):
        # Create a new task
        res = client.post("/tasks", json={"title": "Persistent Task"})
        self.assertEqual(res.status_code, 201)
        created_id = res.json()["id"]

        # Simulate app restart by re-initializing DB table without resetting seed
        # Querying direct from database proves data persistence
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (created_id,))
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row["title"], "Persistent Task")

if __name__ == "__main__":
    unittest.main()
