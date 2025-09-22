from database import pool_getter, _TaskDTO
from models import _InstanceSupportsSequence, AddTaskModel, _TaskUpdateInfoDTO, _TaskDoneDTO, _ModelSupportsSequence
import typing
from loguru import logger as log
from uow import get_uow, UnitOfWork

class CoreDBRepository:
    _uow: typing.ClassVar[typing.Callable[[], typing.AsyncGenerator[UnitOfWork | None]]] = get_uow

    def __init__(self) -> None:
        # self.pool_getter: typing.Callable[typing.AsyncGenerator[asyncpg.pool.Pool, None]] = pool_getter
        self.uow: typing.Callable[[], typing.AsyncGenerator[UnitOfWork, None]] = get_uow
        self.model: typing.Type[_ModelSupportsSequence] = AddTaskModel
        self.return_dto: typing.Type[typing.TypedDict] = _TaskDTO
        self.log = log
        self.update_done_dto: typing.Type[_InstanceSupportsSequence] = _TaskDoneDTO
        self.update_info_dto: typing.Type[_InstanceSupportsSequence] = _TaskUpdateInfoDTO

    async def transaction(self) -> UnitOfWork | None:
        async for uow in self.__class__._uow():
            return uow
        return None

    async def add(
            self,
            task: AddTaskModel
    ) -> _TaskDTO:
        async with await self.transaction() as uow:
            await uow.execute(
                    "INSERT INTO tasks VALUES ($1, $2, $3, $4, $5)",
                    *task.__to_args__
            )
            row = await uow.fetchrow(
                    "SELECT * FROM tasks WHERE id=$1",
                    task.id
                )
        return self.return_dto(**row)

    async def get(
            self,
            task_id: int
    ) -> _TaskDTO:
        async with await self.transaction() as uow:
            row = await uow.fetchrow(
                "SELECT * FROM tasks WHERE id=$1",
                task_id
            )
        return self.return_dto(**row)

    async def delete(
            self,
            task_id: int
    ) -> _TaskDTO:
        try:
            async with await self.transaction() as uow:
                row = await uow.fetchrow(
                        "SELECT * FROM tasks WHERE id=$1",
                        task_id
                )
                await uow.execute(
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
        async with await self.transaction() as uow:
                seq = task.__sequence_fields__
                set_ = ", ".join(
                    [
                        f"{seq[i]}=${i+2}" for i in range(len(seq))
                    ]
                )
                self.log.warning(f"SET = {set_}")
                await uow.execute(
                    f"UPDATE tasks SET {set_} WHERE id=$1",
                    *task.__to_args__
                )
                row = await uow.fetchrow(
                    "SELECT * FROM tasks WHERE id=$1",
                    task.id
                )
        return self.return_dto(**row)
