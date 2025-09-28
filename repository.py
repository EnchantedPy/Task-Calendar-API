from dto import TaskDTO, TaskUpdateDTO, AddTaskDTO
import typing
from loguru import logger as log
from uow import UnitOfWork
from models import BaseAbstractModel

class BaseRepository:
    def __init__(
            self,
            return_dto: typing.Type[typing.TypedDict],
            table: str
    ) -> None:
        self.uow: typing.Callable[[], UnitOfWork | None] = UnitOfWork.instance
        self.return_dto: typing.Type[typing.TypedDict] = return_dto
        self.table: str = table
        self.log = log

    async def transaction(self) -> UnitOfWork:
        return self.uow()


class TaskRepository(BaseRepository):

    def __init__(
            self,
            model: typing.Type[BaseAbstractModel]
    ) -> None:
        super().__init__(TaskDTO, model.__table__)

    async def add(
            self,
            task: AddTaskDTO
    ) -> TaskDTO:
        async with await self.transaction() as uow:
            serial = await uow.fetchrow(
                    f"""
                    INSERT INTO {self.table} (title, description) VALUES ($1, $2) RETURNING id;
                    """,
              task.title, task.description
            )
            row = await uow.fetchrow(
                    f"SELECT * FROM {self.table} WHERE id=$1",
                    serial["id"]
                )
        return self.return_dto(**row)

    async def get(
            self,
            task_id: int
    ) -> TaskDTO:
        async with await self.transaction() as uow:
            row = await uow.fetchrow(
                f"SELECT * FROM {self.table} WHERE id=$1",
                task_id
            )
        return self.return_dto(**row)

    async def delete(
            self,
            task_id: int
    ) -> TaskDTO:
        async with await self.transaction() as uow:
            row = await uow.fetchrow(
                    f"SELECT * FROM {self.table} WHERE id=$1",
                    task_id
            )
            await uow.execute(
                    f"DELETE FROM {self.table} WHERE id=$1",
                    task_id
            )
        return self.return_dto(**row)

    async def update(
            self,
            task: TaskUpdateDTO
    ) -> TaskDTO:
        async with await self.transaction() as uow:
                await uow.execute(
                    f"UPDATE {self.table} SET (title=$2, description=$3, done=$4) WHERE id=$1",
                    task.id, task.title, task.description, task.done
                )
                row = await uow.fetchrow(
                    f"SELECT * FROM {self.table} WHERE id=$1",
                    task.id
                )
        return self.return_dto(**row)
