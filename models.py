import datetime
import typing
import uuid

from pydantic import BaseModel, Field

import functools

class _InstanceSupportsSequence(BaseModel):
    @property
    def __sequence_fields__(self) -> typing.Sequence[str]:
        return [
            name for name in self.__dict__.keys() if name != "id"
        ]

    @property
    def __to_args__(self) -> typing.Tuple[
        typing.Any, ...
    ]:
        return tuple(
            val for val in self.__dict__.values()
        )

Task: typing.Literal["CalendarClass", "TaskClass"] = "TaskClass"

CalendarNote: typing.Literal["CalendarClass", "TaskClass"] = "CalendarClass"

Models: dict[
    str,
    typing.Literal[
        "Task",
        "CalendarNote"
    ]
] = {
    "TaskClass": "Task",
    "CalendarClass": "CalendarNote"
}

class IDFactory:
    __models: typing.ClassVar[dict[str, int | None]] = {
        model: None for model in Models.values()
    }
    id: typing.ClassVar[int | None] = None

    @classmethod
    def get(
    cls,
    model: typing.Literal[
            "Task",
            "CalendarNote"
        ]
    ) -> int:
        if cls.__models[model] is None:
            cls.__models[model] = 0
        cls.__models[model] += 1
        return cls.__models[model]


class _ModelSupportsSequence(BaseModel):

    @classmethod
    def __sequence_fields__(cls) -> typing.Sequence[typing.Tuple[str, str]]:
        return [
            (name, typ.__name__.lower())
            for name, typ in cls.__annotations__.items()
        ]

    @property
    def __to_args__(self) -> typing.Tuple[
        typing.Any, ...
    ]:
        return tuple(
            item for item in self.__dict__.values()
        )


class _TaskModel(_ModelSupportsSequence):
    id: int = Field(
        default_factory=functools.partial(IDFactory.get, Models[Task]),
    )
    title: str
    description: str
    done: bool = Field(
        default=False
    )

    uid: uuid.UUID
    # uid: uuid.UUID = Field(
    #     default_factory=uuid.uuid4
    # )

class AddTaskModel(_TaskModel):
    pass

class _TaskUpdateInfoDTO(_InstanceSupportsSequence):
    id: int
    title: str
    description: str

class _TaskDoneDTO(_InstanceSupportsSequence):
    id: int
    done: bool

class _CalendarNoteModel(_ModelSupportsSequence):
    id: int = Field(
        default_factory=functools.partial(IDFactory.get, Models[CalendarNote]),
    )

    uid: uuid.UUID
    # uid: uuid.UUID = Field(
    #     default_factory=uuid.uuid4
    # )

    date: datetime.datetime
    # date: datetime.datetime = Field(
    #     default_factory=functools.partial(datetime.datetime.now, datetime.timezone.utc),
    # )

    title: str

    note: str

class AddCalendarNoteModel(_CalendarNoteModel):
    pass
