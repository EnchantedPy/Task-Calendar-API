import asyncpg
from database import pool_getter, AddTaskModel, _TaskDTO, _ModelSupportsSequence
import typing

class CoreDBRepository:
    def __init__(self) -> None:
        self.pool_getter: typing.AsyncGenerator[asyncpg.pool.Pool, None] = pool_getter
        self.model: typing.Type[_ModelSupportsSequence] = AddTaskModel
        self.return_dto: typing.Type[typing.TypedDict] = _TaskDTO

    async def __pool(self) -> asyncpg.pool.Pool | None:
        __instance = self.pool_getter()
        pool = await __instance.__anext__()
        return pool

    async def add(
            self,
            task: AddTaskModel
    ) -> _TaskDTO:
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
        return self.return_dto(**row)

    async def get(
            self,
            task_id: int
    ) -> _TaskDTO:
        pool = await self.__pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                row = await conn.fetchrow(
                    "SELECT * FROM tasks WHERE id=$1",
                    task_id
                )
        return self.return_dto(**row)
