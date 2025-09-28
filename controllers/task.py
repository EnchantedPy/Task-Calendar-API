from litestar import Controller, get, post, delete, patch
from litestar.di import Provide
from repository import TaskRepository
from dto import TaskDTO, AddTaskDTO, TaskUpdateDTO
from pydantic import BaseModel, Field
from models import _TaskModel

class TaskGet(BaseModel):
    id: int = Field(
        gt=0
    )

class TaskDel(BaseModel):
    id: int = Field(
        gt=0
    )

class TaskUpdateInfo(BaseModel):
    id: int = Field(
        gt=0
    )
    title: str
    description: str

class TaskMarkDone(BaseModel):
    id: int = Field(
        gt=0
    )

class TaskController(Controller):
    path = "/tasks"
    dependencies = {
        "repo": Provide(lambda: TaskRepository(_TaskModel), sync_to_thread=False),
    }

    # to POST
    @get("/add", tags=["DB"])
    async def add_task(self, repo: TaskRepository) -> TaskDTO:
        return await repo.add(
            AddTaskDTO(
                title="Some task",
                description="Some description",
            )
        )

    @post("/get", tags=["DB"])
    async def get_task(self, data: TaskGet, repo: TaskRepository) -> TaskDTO:
        return await repo.get(
            data.id
        )

    @delete("/delete", tags=["DB"], status_code=200)
    async def delete_task(self, data: TaskDel, repo: TaskRepository) -> TaskDTO:
        return await repo.delete(
            data.id
        )

    @patch("/update", tags=["DB"])
    async def update_task(self, data: TaskUpdateInfo, repo: TaskRepository) -> TaskDTO:
        return await repo.update(
                TaskUpdateDTO(
                    **data.model_dump()
                )
        )

    @patch("/done", tags=["DB"])
    async def done_task(self, data: TaskMarkDone, repo: TaskRepository) -> TaskDTO:
        dict_ = dict(**data.model_dump())
        dict_["done"] = True
        return await repo.update(
            TaskUpdateDTO(**dict_)
        )