from typing import Optional, Protocol


class TaskRepository(Protocol):
    def list_all(self) -> list[dict]:
        ...

    def get(self, task_id: int) -> Optional[dict]:
        ...

    def create(self, title: str) -> dict:
        ...

    def update(self, task_id: int, title: str, done: bool) -> dict:
        ...

    def delete(self, task_id: int) -> bool:
        ...
