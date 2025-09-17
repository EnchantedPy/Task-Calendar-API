import asyncpg
from database import pool_getter, AddTaskModel, _AddTaskDict

class CoreDBRepository:
    def __init__(self) -> None:
        self.pool: asyncpg.pool.Pool | None = None

    async def add(
            self,
            task: AddTaskModel
    ) -> _AddTaskDict | None:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO tasks VALUES ($1, $2, $3, $4, $5)",
                    **task.__to_dict__
                )
                row = await conn.fetchrow(
                    "SELECT * FROM tasks WHERE id=$1",
                    task.id
                )
        return _AddTaskDict(dict(row)) if row else None
