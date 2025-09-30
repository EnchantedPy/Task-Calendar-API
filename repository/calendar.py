from db.models import BaseAbstractModel
from repository import BaseRepository
from dto import CalendarNoteDTO, CalendarNoteUpdateDTO, AddCalendarNoteDTO
import typing

class CalendarNoteRepository(BaseRepository):

    def __init__(
            self,
            model: typing.Type[BaseAbstractModel]
    ) -> None:
        super().__init__(CalendarNoteDTO, model.__table__)

    async def add(self, note: AddCalendarNoteDTO) -> CalendarNoteDTO:
        async with await self.transaction() as uow:
            row = await uow.fetchrow(
                f"INSERT INTO {self.table} (title, note) VALUES ($1, $2) RETURNING *;",
                note.title, note.note
            )
        return self.return_dto(**row)


    async def get(self, note_id: int) -> CalendarNoteDTO:
        async with await self.transaction() as uow:
            row = await uow.fetchrow(
                f"SELECT * FROM {self.table} WHERE id = $1;",
                note_id
            )
        return self.return_dto(**row)

    async def delete(self, note_id: int) -> CalendarNoteDTO:
        async with await self.transaction() as uow:
            row = await uow.fetchrow(
                f"DELETE FROM {self.table} WHERE id = $1 RETURNING *;",
                note_id
            )
        return self.return_dto(**row)

    async def update(self, task: CalendarNoteUpdateDTO) -> CalendarNoteDTO:
        async with await self.transaction() as uow:
            row = await uow.fetchrow(
                f"UPDATE {self.table} SET title = $2, note = $3 WHERE id = $1 RETURNING *;",
                task.id, task.title, task.note
            )
        return self.return_dto(**row)