from dto import TaskDTO, TaskUpdateDTO, AddTaskDTO
import typing
from loguru import logger as log
from db.models import BaseAbstractModel
from repository import BaseRepository

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
                    f"DELETE FROM {self.table} WHERE id=$1 RETURNING id;",
                    task_id
            )
        return self.return_dto(**row)

    async def update(
            self,
            task: TaskUpdateDTO
    ) -> TaskDTO:
        async with await self.transaction() as uow:
                row = await uow.fetchrow(
                    f"UPDATE {self.table} SET title=$2, description=$3, done=$4 WHERE id=$1 RETURNING *;",
                    task.id, task.title, task.description, task.done
                )
        return self.return_dto(**row)
