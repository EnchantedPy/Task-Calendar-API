import asyncpg
from database import pool_getter, AddTaskModel, _AddTaskDict
import pydantic
import typing

class CoreDBRepository:
    def __init__(self) -> None:
        self.pool_getter: typing.AsyncGenerator[asyncpg.pool.Pool, None] = pool_getter
        self.model: pydantic.BaseModel = AddTaskModel

    # def __call__(self) -> None:
    #     self.pool = pool_getter()

    async def __pool(self) -> asyncpg.pool.Pool | None:
        __instance = self.pool_getter()
        pool = await __instance.__anext__()
        return pool

    async def add(
            self,
            task: AddTaskModel
    ) -> _AddTaskDict | None:
        pool = await self.__pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO tasks VALUES ($1, $2, $3, $4, $5)",
                    *task.__to_args__
                )
                row = await conn.fetchrow(
                    "SELECT * FROM tasks WHERE id=$1",
                    task.id
                )
        return _AddTaskDict(dict(row)) if row else None
