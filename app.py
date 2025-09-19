import typing
from litestar import Litestar, get, post, delete, patch, Controller
import repository
from settings import settings
from repository import CoreDBRepository, _TaskDTO
import repository
from pydantic import BaseModel, Field

class ASGILifespan:

    @staticmethod
    async def startup() -> None:
        from database import mgr_getter
        __instance = await mgr_getter().__anext__()
        await __instance.create_tables(
            tables=["tasks"],
            _models=[repository.AddTaskModel]
        )

    @staticmethod
    async def shutdown() -> None:
        from database import mgr_getter
        __instance = await mgr_getter().__anext__()
        await __instance.drop_tables(
            tables=["tasks"]
        )

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
    done: bool

@get("/", tags=["Litestar"])
async def index() -> typing.Dict[str, str]:
    return {"status": "ok"}

@get("/postgres/url", tags=["DB"])
async def postgres_url() -> typing.Dict[str, str]:
    return {
        "url": settings.postgres_url
    }

class TasksController(Controller):
    path = "/tasks"

    # to POST
    @get("/add", tags=["DB"])
    async def add_task(self) -> _TaskDTO:
        repo = CoreDBRepository()
        return await repo.add(
            repo.model(
                title="Some task",
                description="Some description",
            )
        )

    @post("/get", tags=["DB"])
    async def get_task(self, data: TaskGet) -> _TaskDTO:
        repo = CoreDBRepository()
        return await repo.get(
            data.id
        )

    @delete("/delete", tags=["DB"], status_code=200)
    async def delete_task(self, data: TaskDel) -> _TaskDTO:
        repo = CoreDBRepository()
        return await repo.delete(
            data.id
        )

    @patch("/update", tags=["DB"])
    async def update_task(self, data: TaskUpdateInfo) -> _TaskDTO:
        repo = CoreDBRepository()
        return await repo.update(
            repo.update_info_dto(**data.model_dump())
        )

    @patch("/done", tags=["DB"])
    async def done_task(self, data: TaskMarkDone) -> _TaskDTO:
        repo = CoreDBRepository()
        return await repo.update(
            repo.update_done_dto(**data.model_dump())
        )

app = Litestar(
    route_handlers=[index, postgres_url, TasksController],
    on_startup=[ASGILifespan.startup],
    on_shutdown=[ASGILifespan.shutdown],
    debug=True
)