import typing

from IPython.terminal.shortcuts.auto_match import auto_match_parens_raw_string
from pydantic import BaseModel
import db.types as types
from loguru import logger as log

class BaseAbstractModel:
    __tables: typing.ClassVar[list[str]]
    __models: typing.ClassVar[list[typing.Type["BaseAbstractModel"]]]
    __pre_assigned: typing.ClassVar[dict[str, str]] = {}

    @classmethod
    def tables(cls) -> list[str]:
        return cls.__tables

    @classmethod
    def models(cls) -> list[typing.Type["BaseAbstractModel"]]:
        return cls.__models

    @classmethod
    def pre_assigned(cls) -> dict[str, str]:
        return cls.__pre_assigned

    @classmethod
    def pre_assign(cls, k: str, v: str) -> None | bool:
        """
        Value here can't be overridden
        """
        if cls.__pre_assigned[k]:
            return False
        cls.__pre_assigned[k] = v
        return None

    def __init_subclass__(cls, **kw) -> None:
        super().__init_subclass__(**kw)
        for attr, anno in cls.__annotations__.items():
            try:
                if attr == "__table__":
                    BaseAbstractModel.__tables.append(attr)
                BaseAbstractModel.__models.append(cls)
            except Exception as e:
                raise e
            log.warning(
                f"__init_subclass__ - setting {attr} to {anno}"
            )
            if not hasattr(cls, attr):
                if isinstance(anno, type):
                    instance = anno()
                    setattr(cls, attr, instance)
                    log.warning(
                        f"__init_subclass__ - set {attr} to {instance} (id: {id(instance)})"
                    )
            else:
                log.warning(
                    f"__init_subclass__ - skipping {attr}, already set to {getattr(cls, attr)} (id: {id(getattr(cls, attr))})"
                )

        def __sequence_fields__(cls) -> typing.Sequence[tuple[str, types.AbstractDBType]]:
            returning = [
                (attribute, getattr(cls, attribute))
                for attribute in cls.__annotations__
                if callable(getattr(cls, attribute))
            ]
            for attr in cls.__annotations__:
                val = getattr(cls, attr)
                log.warning(f"{attr} -> {val} (id: {id(val)})")
            return returning

        def __to_args__(self) -> typing.Tuple[
            typing.Any, ...
        ]:
            return tuple(
                item for item in self.__dict__.values()
            )

        def __sequence_indexes__(cls) -> typing.Sequence[str] | typing.Iterable[str]:
            returning = []
            for attr, val in cls.__annotations__.items():
                if val is not None and hasattr(cls, attr):
                    instance = getattr(cls, attr)
                    if instance.__index__():
                        returning.append(attr)

            return returning

        cls.__sequence_indexes__ = classmethod(__sequence_indexes__)
        cls.__sequence_fields__ = classmethod(__sequence_fields__)
        cls.__to_args__ = property(__to_args__)

class _TaskModel(BaseAbstractModel):
    __table__ = "tasks"

    id: types.Integer = types.Integer(
        autoincrement=True,
        index=True,
        unique=True,
        nullable=False,
        pk=True
    )
    title: types.String = types.String(
        index=True,
        unique=True,
        nullable=False
    )
    description: types.String = types.String(
        nullable=True
    )
    done: types.Boolean = types.Boolean(
        default="false"
    )
    uid: types.UUID = types.UUID(
        index=True,
        unique=True,
        nullable=False,
        pk=True,
        default="uuid_generate_v4()"
    )

class _InstanceSupportsSequence(BaseModel):
    @property
    def __sequence_fields__(self) -> typing.Sequence[str] | typing.Iterable[str]:
        return [
            attr for attr in self.__dict__.keys() if attr not in BaseAbstractModel.pre_assigned()
        ]

    @property
    def __to_args__(self) -> typing.Tuple[
        typing.Any, ...
    ]:
        return tuple(
            val for _, val in self.__dict__.items() if _ not in BaseAbstractModel.pre_assigned()
        )

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

class _CalendarNoteModel(BaseAbstractModel):
    __table__ = "calendar_notes"

    id: types.Integer = types.Integer(
        index=True,
        unique=True,
        nullable=False,
        autoincrement=True,
        pk=True
    )
    uid: types.UUID = types.UUID(
        index=True,
        unique=True,
        nullable=False,
        pk=True
    )
    date: types.DateTime = types.DateTime(
        default="now()"
    )
    title: types.String = types.String(
        unique=True
    )
    note: types.String = types.String(
        nullable=True
    )

class AddCalendarNoteModel(_InstanceSupportsSequence):
    pass # NotImplemented
