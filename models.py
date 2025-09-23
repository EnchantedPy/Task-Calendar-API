import datetime
import typing
import uuid
from pydantic import BaseModel, Field
import db.types as types

class _InstanceSupportsSequence(BaseModel):
    @property
    def __sequence_fields__(self) -> typing.Sequence[str] | typing.Iterable[str]:
        return [
            name for name in self.__dict__.keys() if name != "id" or name != "uid"
        ]

    @property
    def __to_args__(self) -> typing.Tuple[
        typing.Any, ...
    ]:
        return tuple(
            val for _, val in self.__dict__.items() if _ != "id" or _ != "uid"
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


# class _ModelSupportsSequence(BaseModel):
#
#     @classmethod
#     def __sequence_fields__(cls) -> typing.Sequence[typing.Tuple[str, str]]:
#         return [
#             (name, typ.__name__.lower())
#             for name, typ in cls.__annotations__.items()
#         ]
#
#     @property
#     def __to_args__(self) -> typing.Tuple[
#         typing.Any, ...
#     ]:
#         return tuple(
#             item for item in self.__dict__.values()
#         )

class _BaseAbstractModel:
    def __init_subclass__(cls, **kw) -> None:
        super().__init_subclass__(**kw)
        for attr, anno in cls.__annotations__.items():
            if not hasattr(cls, attr):
                if isinstance(anno, type):
                    setattr(cls, attr, anno())

        def __sequence_fields__(cls) -> typing.Sequence[tuple[str, str]]:
            return [
                (attribute, getattr(cls, attr).__call__())
                for attribute in cls.__annotations__
                if callable(getattr(cls, attribute))
            ]

        def __to_args__(self) -> typing.Tuple[
            typing.Any, ...
        ]:
            return tuple(
                item for item in self.__dict__.values()
            )

        cls.__sequence_fields__ = classmethod(__sequence_fields__)
        cls.__to_args__ = property(__to_args__)

class _TaskModel(_BaseAbstractModel):
    id: types.Integer = types.Integer(index=True)
    title: types.String
    description: types.String
    done: types.Boolean
    uid: types.UUID = types.UUID(index=True)


# class _TaskModel(_ModelSupportsSequence):
#     id: int
#     # id: int = Field(
#     #     default_factory=functools.partial(IDFactory.get, Models[Task]),
#     # )
#     title: str
#     description: str
#     done: bool
#
#     uid: uuid.UUID
#     # uid: uuid.UUID = Field(
#     #     default_factory=uuid.uuid4
#     # )

class AddTaskModel(_InstanceSupportsSequence):
    title: str
    description: str

class _TaskUpdateInfoDTO(_InstanceSupportsSequence):
    id: int
    title: str
    description: str

class _TaskDoneDTO(_InstanceSupportsSequence):
    id: types.Integer = types.Integer(index=True)
    done: types.Boolean

class _CalendarNoteModel(_BaseAbstractModel):
    id: int
    # id: int = Field(
    #     default_factory=functools.partial(IDFactory.get, Models[CalendarNote]),
    # )

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

class AddCalendarNoteModel(_InstanceSupportsSequence):
    pass # NotImplemented
