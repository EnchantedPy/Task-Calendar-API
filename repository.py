from db.manager import _TaskDTO
from models import _InstanceSupportsSequence, AddTaskModel, _TaskUpdateInfoDTO, _TaskDoneDTO
import typing
from loguru import logger as log
from uow import UnitOfWork

class CoreDBRepository:
    def __init__(self) -> None:
        self.uow: typing.Callable[[], UnitOfWork | None] = UnitOfWork.instance
        self.model: typing.Type[_InstanceSupportsSequence] = AddTaskModel
        self.return_dto: typing.Type[typing.TypedDict] = _TaskDTO
        self.log = log
        self.update_done_dto: typing.Type[_InstanceSupportsSequence] = _TaskDoneDTO
        self.update_info_dto: typing.Type[_InstanceSupportsSequence] = _TaskUpdateInfoDTO

    async def transaction(self) -> UnitOfWork:
        return self.uow()

    async def add(
            self,
            task: AddTaskModel
    ) -> _TaskDTO:
        async with await self.transaction() as uow:
            placeholder_list = [f"${i+1}" for i in range(len(task.__to_args__))]
            query = f"INSERT INTO tasks ({", ".join(field for field in task.__sequence_fields__)}) VALUES ({", ".join(placeholder_list)}) RETURNING id"
            # self.log.warning(query)
            # self.log.warning(task.__to_args__)
            serial = await uow.fetchrow(
                    query,
                *task.__to_args__
            )
            row = await uow.fetchrow(
                    "SELECT * FROM tasks WHERE id=$1",
                    serial["id"]
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
                # self.log.warning(f"SET = {set_}")
                await uow.execute(
                    f"UPDATE tasks SET {set_} WHERE id=$1",
                    *task.__to_args__
                )
                row = await uow.fetchrow(
                    "SELECT * FROM tasks WHERE id=$1",
                    task.id
                )
        return self.return_dto(**row)
