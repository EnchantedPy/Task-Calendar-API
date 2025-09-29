import typing
from litestar import Litestar, get
from core.settings import settings
from core.lifespan import ASGILifespan
from controllers import TaskController, CalendarController

@get("/", tags=["Litestar"])
async def index() -> typing.Dict[str, str]:
    return {"status": "ok"}

@get("/postgres/url", tags=["DB"])
async def postgres_url() -> typing.Dict[str, str]:
    return {
        "url": settings.postgres_url
    }

app = Litestar(
    route_handlers=[index, postgres_url, TaskController, CalendarController],
    on_startup=[ASGILifespan.startup],
    on_shutdown=[ASGILifespan.shutdown],
    debug=True
)