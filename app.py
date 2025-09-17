import typing
from litestar import Litestar, get

import repository
from settings import settings
from repository import CoreDBRepository
import repository

class ASGILifespan:

    @staticmethod
    async def startup() -> None:
        from database import mgr_getter
        await mgr_getter().create_tables(
            tables=["tasks"],
            _models=[repository.AddTaskModel]
        )

    @staticmethod
    async def shutdown() -> None:
        from database import mgr_getter
        await mgr_getter().drop_tables()

@get("/", tags=["Litestar"])
async def index() -> typing.Dict[str, str]:
    return {"status": "ok"}

@get("/postgres/url", tags=["DB"])
async def postgres_url() -> typing.Dict[str, str]:
    return {
        "url": settings.postgres_url
    }

app = Litestar(
    route_handlers=[index, postgres_url],
    on_startup=ASGILifespan.startup,
    on_shutdown=ASGILifespan.shutdown,
)