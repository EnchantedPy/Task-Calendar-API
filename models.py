import typing
from pydantic import BaseModel
import db.types as types

class BaseAbstractModel:
    _tables: typing.ClassVar[list[str]] = []
    _models: typing.ClassVar[list[typing.Type["BaseAbstractModel"]]] = []
    _pre_assigned: typing.ClassVar[list[str]] = []

    @classmethod
    def __cls_repr__(cls) -> str:
        return cls.__name__

    @classmethod
    def tables(cls) -> list[str]:
        return cls._tables

    @classmethod
    def assign_table(cls, table: str) -> None:
        cls._tables.append(table)

    @classmethod
    def models(cls) -> list[typing.Type["BaseAbstractModel"]]:
        return cls._models

    @classmethod
    def assign_model(cls, model: typing.Type["BaseAbstractModel"]) -> None:
        cls._models.append(model)

    @classmethod
    def pre_assigned(cls) -> list[str]:
        return cls._pre_assigned

    @classmethod
    def pre_assign(cls, attr: str) -> None:
        cls._pre_assigned.append(attr)

    def __init_subclass__(cls, **kw) -> None:
        super().__init_subclass__(**kw)

        BaseAbstractModel.assign_table(getattr(cls, '__table__'))
        BaseAbstractModel.assign_model(cls)

        for attr, anno in cls.__annotations__.items():
            existing_val = getattr(cls, attr, None)
            if isinstance(existing_val, anno):
                pass
            else:
                field_instance = anno()
                setattr(cls, attr, field_instance)

            if getattr(cls, attr).__unique__() or getattr(cls, attr).__pk__():
                BaseAbstractModel.pre_assign(attr)

        def __sequence_fields__(cls) -> typing.Sequence[tuple[str, types.AbstractDBType]]:
            returning = [
                (attribute, getattr(cls, attribute))
                for attribute in cls.__annotations__
                if callable(getattr(cls, attribute))
            ]
            for attr in cls.__annotations__:
                val = getattr(cls, attr)
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
                    if attr in BaseAbstractModel.pre_assigned():
                        continue
                    elif attr == "__table__":
                        continue
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
        index=True, # remove later
        unique=True, # remove later
        nullable=False,
        default="New task"
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
    )
    date: types.DateTime = types.DateTime(
        default="now()"
    )
    title: types.String = types.String(
        default="New note"
    )

    note: types.String = types.String(
        nullable=True
    )

class AddCalendarNoteModel(_InstanceSupportsSequence):
    pass # NotImplemented
