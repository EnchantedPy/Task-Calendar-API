from dto import TaskDTO, TaskUpdateDTO, AddTaskDTO
import typing
from loguru import logger as log
from db.uow import UnitOfWork
from db.models import BaseAbstractModel

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