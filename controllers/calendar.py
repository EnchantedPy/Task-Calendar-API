from litestar import Controller, post, put, delete
from litestar.di import Provide
from repository import CalendarNoteRepository
from db.models import _CalendarNoteModel
from pydantic import BaseModel, Field
from dto import CalendarNoteDTO, CalendarNoteUpdateDTO, AddCalendarNoteDTO

class CalendarNoteAdd(BaseModel):
    title: str = "New note"
    note: str

class CalendarNoteGet(BaseModel):
    id: int = Field(
        gt=0
    )

class CalendarNoteDel(BaseModel):
    id: int = Field(
        gt=0
    )

class CalendarNoteUpdate(BaseModel):
    id: int = Field(
        gt=0
    )
    title: str
    note: str

class CalendarController(Controller):
    path = "/calendar"
    dependencies = {
        "repo": Provide(lambda: CalendarNoteRepository(_CalendarNoteModel), sync_to_thread=False),
    }

    @post("/add", tags=["Calendar notes"])
    async def add_calendar_note(self, data: CalendarNoteAdd, repo: CalendarNoteRepository) -> CalendarNoteDTO:
        return await repo.add(
            AddCalendarNoteDTO(
                title=data.title,
                note=data.note
            )
        )

    @post("/get", tags=["Calendar notes"])
    async def get_calendar_note(self, data: CalendarNoteGet, repo: CalendarNoteRepository) -> CalendarNoteDTO:
        return await repo.get(
            data.id
        )

    @delete("/delete", tags=["Calendar notes"], status_code=200)
    async def delete_calendar_note(self, data: CalendarNoteDel, repo: CalendarNoteRepository) -> CalendarNoteDTO:
        return await repo.delete(
            data.id
        )

    @put("/update", tags=["Calendar notes"])
    async def update_calendar_note(self, data: CalendarNoteUpdate, repo: CalendarNoteRepository) -> CalendarNoteDTO:
        return await repo.update(
            CalendarNoteUpdateDTO(
                id=data.id,
                title=data.title,
                note=data.note
            )
        )
