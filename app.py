import typing
from litestar import Litestar, get

import repository
from settings import settings
from repository import CoreDBRepository, _AddTaskDict
import repository

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

@get("/", tags=["Litestar"])
async def index() -> typing.Dict[str, str]:
    return {"status": "ok"}

@get("/postgres/url", tags=["DB"])
async def postgres_url() -> typing.Dict[str, str]:
    return {
        "url": settings.postgres_url
    }

@get("/test/repo", tags=["DB"])
async def test_repo() -> _AddTaskDict | None:
    repo = CoreDBRepository()
    return await repo.add(
        repo.model(
            title="Some task",
            description="Some description",
        )
    )

app = Litestar(
    route_handlers=[index, postgres_url, test_repo],
    on_startup=[ASGILifespan.startup],
    on_shutdown=[ASGILifespan.shutdown],
    debug=True
)