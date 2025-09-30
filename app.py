import typing
from litestar import Litestar, get
from core.lifespan import ASGILifespan
from controllers import TaskController, CalendarController
from core.exceptions import (
    unique_violation_handler, foreign_key_violation_handler, postgres_error_handler
)
from asyncpg.exceptions import (
    UniqueViolationError,
    ForeignKeyViolationError,
    PostgresError,
)

@get("/", tags=["Litestar"])
async def index() -> typing.Dict[str, str]:
    return {"status": "ok"}

app = Litestar(
    route_handlers=[index, TaskController, CalendarController],
    on_startup=[ASGILifespan.startup],
    on_shutdown=[ASGILifespan.shutdown],
    exception_handlers={
        UniqueViolationError: unique_violation_handler,
        ForeignKeyViolationError: foreign_key_violation_handler,
        PostgresError: postgres_error_handler,
    },
    debug=True
)