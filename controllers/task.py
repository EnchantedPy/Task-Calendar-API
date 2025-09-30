from litestar import Controller, post, delete, put
from litestar.di import Provide
from repository import TaskRepository
from dto import TaskDTO, AddTaskDTO, TaskUpdateDTO
from pydantic import BaseModel, Field
from db.models import _TaskModel

class TaskAdd(BaseModel):
    title: str = "New task"
    description: str

class TaskGet(BaseModel):
    id: int = Field(
        gt=0
    )

class TaskDel(BaseModel):
    id: int = Field(
        gt=0
    )

class TaskUpdate(BaseModel):
    id: int = Field(
        gt=0
    )
    title: str
    description: str
    done: bool

class TaskController(Controller):
    path = "/tasks"
    dependencies = {
        "repo": Provide(lambda: TaskRepository(_TaskModel), sync_to_thread=False),
    }

    @post("/add", tags=["Tasks"])
    async def add_task(self, data: TaskAdd, repo: TaskRepository) -> TaskDTO:
        return await repo.add(
            AddTaskDTO(
                title=data.title,
                description=data.description,
            )
        )

    @post("/get", tags=["Tasks"])
    async def get_task(self, data: TaskGet, repo: TaskRepository) -> TaskDTO:
        return await repo.get(
            data.id
        )

    @delete("/delete", tags=["Tasks"], status_code=200)
    async def delete_task(self, data: TaskDel, repo: TaskRepository) -> TaskDTO:
        return await repo.delete(
            data.id
        )

    @put("/update", tags=["Tasks"])
    async def update_task(self, data: TaskUpdate, repo: TaskRepository) -> TaskDTO:
        return await repo.update(
                TaskUpdateDTO(
                    data.id, data.title, data.description, data.done
                )
        )