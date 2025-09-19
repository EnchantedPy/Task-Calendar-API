import asyncpg
from database import pool_getter, AddTaskModel, _TaskDTO, _ModelSupportsSequence, _InstanceSupportsSequence,  _TaskUpdateInfoDTO, _TaskDoneDTO
import typing
from loguru import logger as log

class CoreDBRepository:
    def __init__(self) -> None:
        self.pool_getter: typing.AsyncGenerator[asyncpg.pool.Pool, None] = pool_getter
        self.model: typing.Type[_ModelSupportsSequence] = AddTaskModel
        self.return_dto: typing.Type[typing.TypedDict] = _TaskDTO
        self.log = log
        self.update_done_dto: typing.Type[_InstanceSupportsSequence] = _TaskDoneDTO
        self.update_info_dto: typing.Type[_InstanceSupportsSequence] = _TaskUpdateInfoDTO

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

    async def delete(
            self,
            task_id: int
    ) -> _TaskDTO:
        pool = await self.__pool()
        try:
            async with pool.acquire() as conn:
                async with conn.transaction():
                    row = await conn.fetchrow(
                        "SELECT * FROM tasks WHERE id=$1",
                        task_id
                    )
                    await conn.execute(
                        "DELETE FROM tasks WHERE id=$1",
                        task_id
                    )
        except Exception:
            raise
        return self.return_dto(**row)

    async def update(
            self,
            task: _TaskUpdateInfoDTO | _TaskDoneDTO
    ) -> _TaskDTO:
        pool = await self.__pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                seq = task.__sequence_fields__
                set_ = ", ".join(
                    [
                        f"{seq[i]}=${i+2}" for i in range(len(seq))
                    ]
                )
                self.log.warning(f"SET = {set_}")
                await conn.execute(
                    f"UPDATE tasks SET {set_} WHERE id=$1",
                    *task.__to_args__
                )
                row = await conn.fetchrow(
                    "SELECT * FROM tasks WHERE id=$1",
                    task.id
                )
        return self.return_dto(**row)
