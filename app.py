import typing
from litestar import Litestar, get, post, delete, patch, Controller
from litestar.di import Provide
from core.settings import settings
from repository import CoreDBRepository, _TaskDTO
from pydantic import BaseModel, Field
from core.lifespan import ASGILifespan

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
    dependencies = {
        "repo": Provide(lambda: CoreDBRepository()),
    }

    # to POST
    @get("/add", tags=["DB"])
    async def add_task(self, repo: CoreDBRepository) -> _TaskDTO:
        return await repo.add(
            repo.model(
                title="Some task",
                description="Some description",
            )
        )

    @post("/get", tags=["DB"])
    async def get_task(self, data: TaskGet, repo: CoreDBRepository) -> _TaskDTO:
        return await repo.get(
            data.id
        )

    @delete("/delete", tags=["DB"], status_code=200)
    async def delete_task(self, data: TaskDel, repo: CoreDBRepository) -> _TaskDTO:
        return await repo.delete(
            data.id
        )

    @patch("/update", tags=["DB"])
    async def update_task(self, data: TaskUpdateInfo, repo: CoreDBRepository) -> _TaskDTO:
        return await repo.update(
            repo.update_info_dto(**data.model_dump())
        )

    @patch("/done", tags=["DB"])
    async def done_task(self, data: TaskMarkDone, repo: CoreDBRepository) -> _TaskDTO:
        dict_ = dict(**data.model_dump())
        dict_["done"] = True
        return await repo.update(
            repo.update_done_dto(**dict_)
        )

app = Litestar(
    route_handlers=[index, postgres_url, TasksController],
    on_startup=[ASGILifespan.startup],
    on_shutdown=[ASGILifespan.shutdown],
    debug=True
)