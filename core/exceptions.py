from litestar.connection import Request
from litestar.response import Response
from litestar.status_codes import (
    HTTP_409_CONFLICT,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from asyncpg.exceptions import (
    UniqueViolationError,
    ForeignKeyViolationError,
    PostgresError,
)

def unique_violation_handler(request: Request, exc: UniqueViolationError) -> Response:
    return Response(
        content={"detail": "Unique constraint violation."},
        status_code=HTTP_409_CONFLICT,
    )


def foreign_key_violation_handler(request: Request, exc: ForeignKeyViolationError) -> Response:
    return Response(
        content={"detail": "Foreign key violation."},
        status_code=HTTP_400_BAD_REQUEST,
    )


def postgres_error_handler(request: Request, exc: PostgresError) -> Response:
    return Response(
        content={"detail": "Unexpected database error."},
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    )

