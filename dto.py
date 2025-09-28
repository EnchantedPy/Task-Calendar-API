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

@dataclass
class AddCalendarNoteDTO:
    pass # NotImplemented