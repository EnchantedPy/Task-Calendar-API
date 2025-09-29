from datetime import datetime
from dataclasses import dataclass
import typing
import uuid
# from typeguard import typechecked

class TaskDTO(typing.TypedDict):
    id: int
    title: str
    description: str
    done: bool
    uid: uuid.UUID

@dataclass
class AddTaskDTO:
    title: str
    description: str

@dataclass
class TaskUpdateDTO:
    id: int
    title: str
    description: str
    done: bool

class CalendarNoteDTO(typing.TypedDict):
    id: int
    uid: uuid.UUID
    date: datetime
    title: str
    note: str

@dataclass
class AddCalendarNoteDTO:
    title: str
    note: str

@dataclass
class CalendarNoteUpdateDTO:
    id: int
    title: str
    note: str