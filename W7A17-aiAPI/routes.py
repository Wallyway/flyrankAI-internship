from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Optional

from service import TaskService

router = APIRouter()


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


def get_service(request: Request) -> TaskService:
    return request.app.state.service


@router.get("/", summary="API info", description="Describes this API and its main endpoints.")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@router.get("/health", summary="Health check", description="Reports whether the server is running.")
def health():
    return {"status": "ok"}


@router.get("/tasks", tags=["tasks"], summary="List tasks", description="Returns every task.")
def list_tasks(service: TaskService = Depends(get_service)):
    return service.list_tasks()


@router.get("/tasks/{task_id}", tags=["tasks"], summary="Get a task", description="Returns a single task by id, or 404 if it does not exist.")
def get_task(task_id: int, service: TaskService = Depends(get_service)):
    return service.get_task(task_id)


@router.post("/tasks", status_code=201, tags=["tasks"], summary="Create a task", description="Creates a task from a title. Rejects a missing or empty title with 400.")
def create_task(task: TaskCreate, service: TaskService = Depends(get_service)):
    return service.create_task(task.title)


@router.put("/tasks/{task_id}", tags=["tasks"], summary="Update a task", description="Replaces title and/or done for a task. 404 unknown id, 400 empty or invalid body.")
def update_task(task_id: int, update: TaskUpdate, service: TaskService = Depends(get_service)):
    return service.update_task(task_id, update.title, update.done)


@router.delete("/tasks/{task_id}", status_code=204, tags=["tasks"], summary="Delete a task", description="Removes a task. 404 if the id does not exist.")
def delete_task(task_id: int, service: TaskService = Depends(get_service)):
    service.delete_task(task_id)
