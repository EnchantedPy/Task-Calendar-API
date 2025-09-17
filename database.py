from collections.abc import Sequence

import asyncpg
from pydantic import BaseModel, Field
from settings import settings
import typing
import uuid

@typing.runtime_checkable
class _ModelNext(typing.Protocol):
    def __next__(self) -> typing.Generator[str]: # model cls attr
        ...

__pool: asyncpg.pool.Pool | None = None
__id: int | None = None
__instance: "AsyncPGPoolManager | None" = None

class AsyncPGPoolManager:
    def __init__(self) -> None:
        self.pool = None

    async def __create_connection_pool() -> asyncpg.pool.Pool:
        return await asyncpg.create_pool(
            user=settings.USER,
            password=settings.PASSWD,
            database=settings.DB,
            host=settings.HOST,
            port=settings.PORT,
            min_size=settings.MIN_POOL,
            max_size=settings.MAX_POOL,
        )

    async def __aenter__(self) -> typing.Self:
        self.pool = await self.__create_connection_pool()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type:
            return False
        return True

    @staticmethod
    def _get_constraints(arg) -> Sequence[str]:
        constraints = []
        if arg == "uuid":
            constraints.append("UNIQUE")
            constraints.append("NOT NULL")
        return constraints


    def _get_attr_type_constraints(self, arg, typ) -> tuple[str, str, Sequence[str]]:
        conventions: dict[str, str] = {
            "int": "INTEGER",
            "pk": "SERIAL PRIMARY KEY",
            "str": "TEXT",
            "bool": "BOOLEAN",
            "uuid": "UUID",
        }
        type_ = "pk" if arg == "id" else typ
        return arg, conventions[type_], self._get_constraints(arg)

    async def create_tables(self, tables: typing.Sequence[str] | typing.Iterable[str], _models: typing.Sequence[BaseModel]) -> bool | typing.NoReturn:
        async with self.__aenter__() as conn:
            try:
                for idx, table in enumerate(tables):
                    columns = [
                        f'{attr} {type_} {" ".join([
                            constraint for constraint in constraints
                        ])}' for attr, type_, constraints in [self._get_attr_type_constraints(arg, typ) for arg, typ in _models[idx].__sequence_fields__]
                    ]
                    await conn.execute(
                        f"""
                            CREATE TABLE IF NOT EXISTS {table} (
                                {", ".join(columns)}
                            );
                        """
                    )
            except Exception as e:
                raise e
            return True

        async def drop_tables(self) -> None:
            ...

async def pool_getter() -> typing.AsyncGenerator[asyncpg.pool.Pool, None]:
    global __pool
    if not __pool:
        async with AsyncPGPoolManager() as mgr:
            __pool = mgr.pool
    yield __pool

async def mgr_getter() -> typing.AsyncGenerator[AsyncPGPoolManager, None]:
    global __instance
    if not __instance:
        __instance = AsyncPGPoolManager()
    yield __instance

def get_id() -> int:
    global __id
    if not __id:
        __id = 0
    __id += 1
    return __id

class AddTaskModel(BaseModel, _ModelNext):
    id: int = Field(
        default_factory=get_id
    )
    title: str
    desc: str
    done: bool
    uuid: uuid.UUID = Field(
        default_factory=uuid.uuid4
    )

    def __iter__(self) -> typing.Generator[str, None]:
        for attr in self.__dict__.keys():
            yield attr

    def __len_fields__(self) -> int:
        _: int = 0
        for attr, _ in self.__dict__.items():
            _ += 1
        return _

    def __sequence_fields__(self) -> Sequence[typing.Tuple[str, str]]:
        return [
            (x, self.__annotations__[x].__name__.lower())
            for x in self.__dict__.keys()
        ]

    @property
    def __to_dict__(self) -> typing.Dict[
        str,
        int | str | bool | uuid.UUID
    ]:
        return {
            "id": self.id,
            "title": self.title,
            "desc": self.desc,
            "done": self.done,
            "uuid": self.uuid,
        }

class _AddTaskDict(typing.TypedDict):
    id: int
    title: str
    desc: str
    done: bool
    uuid: uuid.UUID