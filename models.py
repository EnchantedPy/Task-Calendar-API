import datetime
import typing
import uuid

import loguru
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
            loguru.logger.warning(
                f"__init_subclass__ - setting {attr} to {anno}"
            )
            if not hasattr(cls, attr):
                if isinstance(anno, type):
                    instance = anno()
                    setattr(cls, attr, instance)
                    loguru.logger.warning(
                        f"__init_subclass__ - set {attr} to {instance} (id: {id(instance)})"
                    )
            else:
                loguru.logger.warning(
                    f"__init_subclass__ - skipping {attr}, already set to {getattr(cls, attr)} (id: {id(getattr(cls, attr))})"
                )

        def __sequence_fields__(cls) -> typing.Sequence[tuple[str, str]]:
            returning = [
                (attribute, getattr(cls, attribute).__call__())
                for attribute in cls.__annotations__
                if callable(getattr(cls, attribute))
            ]
            for attr in cls.__annotations__:
                val = getattr(cls, attr)
                loguru.logger.warning(f"{attr} -> {val} (id: {id(val)})")
            return returning

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
    id: int
    done: bool

class _CalendarNoteModel(_BaseAbstractModel):
    id: types.Integer = types.Integer(index=True)
    # id: int = Field(
    #     default_factory=functools.partial(IDFactory.get, Models[CalendarNote]),
    # )

    uid: types.UUID = types.UUID(index=True)
    # uid: uuid.UUID = Field(
    #     default_factory=uuid.uuid4
    # )

    date: types.DateTime
    # date: datetime.datetime = Field(
    #     default_factory=functools.partial(datetime.datetime.now, datetime.timezone.utc),
    # )

    title: types.String

    note: types.String

class AddCalendarNoteModel(_InstanceSupportsSequence):
    pass # NotImplemented
