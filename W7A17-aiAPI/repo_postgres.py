from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from typing import Optional


class PostgresTaskRepository:
    def __init__(self, dsn: str):
        self.pool = ConnectionPool(dsn, kwargs={"row_factory": dict_row}, open=True)

    def list_all(self) -> list[dict]:
        with self.pool.connection() as conn:
            return conn.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()

    def get(self, task_id: int) -> Optional[dict]:
        with self.pool.connection() as conn:
            return conn.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,)).fetchone()

    def create(self, title: str) -> dict:
        with self.pool.connection() as conn:
            return conn.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, FALSE) RETURNING id, title, done",
                (title,),
            ).fetchone()

    def update(self, task_id: int, title: str, done: bool) -> dict:
        with self.pool.connection() as conn:
            return conn.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done",
                (title, done, task_id),
            ).fetchone()

    def delete(self, task_id: int) -> bool:
        with self.pool.connection() as conn:
            return conn.execute("DELETE FROM tasks WHERE id = %s", (task_id,)).rowcount > 0
