import typing
from litestar import Litestar, get
from core.lifespan import ASGILifespan
from controllers import TaskController, CalendarController

@get("/", tags=["Litestar"])
async def index() -> typing.Dict[str, str]:
    return {"status": "ok"}

app = Litestar(
    route_handlers=[index, TaskController, CalendarController],
    on_startup=[ASGILifespan.startup],
    on_shutdown=[ASGILifespan.shutdown],
    debug=True
)