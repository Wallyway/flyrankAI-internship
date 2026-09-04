from fastapi import HTTPException
from typing import Optional

from repository import TaskRepository


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def list_tasks(self) -> list[dict]:
        return self.repository.list_all()

    def get_task(self, task_id: int) -> dict:
        task = self.repository.get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        return task

    def create_task(self, title: str) -> dict:
        if not title.strip():
            raise HTTPException(status_code=400, detail="title is required")
        return self.repository.create(title)

    def update_task(self, task_id: int, title: Optional[str], done: Optional[bool]) -> dict:
        task = self.repository.get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        if title is None and done is None:
            raise HTTPException(status_code=400, detail="title and/or done is required")
        if title is not None and not title.strip():
            raise HTTPException(status_code=400, detail="title cannot be empty")
        new_title = task["title"] if title is None else title
        new_done = task["done"] if done is None else done
        return self.repository.update(task_id, new_title, new_done)

    def delete_task(self, task_id: int):
        if not self.repository.delete(task_id):
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
