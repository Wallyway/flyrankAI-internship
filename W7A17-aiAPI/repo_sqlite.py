from typing import Optional
import sqlite3

SEED_TASKS = [("Buy groceries", 0), ("Write report", 0), ("Walk the dog", 1)]


class SqliteTaskRepository:
    def __init__(self, path: str):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.init_schema()

    def init_schema(self):
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS tasks ("
            "id INTEGER PRIMARY KEY, "
            "title TEXT NOT NULL, "
            "done INTEGER NOT NULL DEFAULT 0)"
        )
        count = self.db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            self.db.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", SEED_TASKS)
        self.db.commit()

    def to_task(self, row) -> dict:
        return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

    def list_all(self) -> list[dict]:
        rows = self.db.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()
        return [self.to_task(row) for row in rows]

    def get(self, task_id: int) -> Optional[dict]:
        row = self.db.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return None if row is None else self.to_task(row)

    def create(self, title: str) -> dict:
        cursor = self.db.execute("INSERT INTO tasks (title, done) VALUES (?, 0)", (title,))
        self.db.commit()
        return {"id": cursor.lastrowid, "title": title, "done": False}

    def update(self, task_id: int, title: str, done: bool) -> dict:
        self.db.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (title, int(done), task_id))
        self.db.commit()
        return {"id": task_id, "title": title, "done": bool(done)}

    def delete(self, task_id: int) -> bool:
        cursor = self.db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.db.commit()
        return cursor.rowcount > 0
