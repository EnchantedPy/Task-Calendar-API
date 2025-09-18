import asyncpg
from pydantic import BaseModel, Field
from settings import settings
import typing
import uuid
from loguru import logger as log

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

class AsyncPGPoolManager:
    __instance: typing.ClassVar["AsyncPGPoolManager | None"] = None

    def __init__(self) -> None:
        self.pool = None
        self.log = log

    @classmethod
    async def get_instance(cls) -> "AsyncPGPoolManager":
        if cls.__instance is None:
            cls.__instance = cls()
            cls.__instance.pool = await cls.__instance.__create_connection_pool()
        return cls.__instance

    async def __create_connection_pool(self) -> asyncpg.pool.Pool:
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
    def _get_constraints(arg) -> typing.Sequence[str]:
        constraints = []
        if arg == "uid":
            constraints.append("UNIQUE")
            constraints.append("NOT NULL")
        return constraints


    def _get_attr_type_constraints(self, arg, typ) -> tuple[str, str, typing.Sequence[str]]:
        conventions: dict[str, str] = {
            "int": "INTEGER",
            "pk": "SERIAL PRIMARY KEY",
            "str": "TEXT",
            "bool": "BOOLEAN",
            "uuid": "UUID",
        }
        type_ = "pk" if arg == "id" else typ
        return arg, conventions[type_], self._get_constraints(arg)

    async def create_tables(self, tables: typing.Sequence[str] | typing.Iterable[str], _models: typing.Sequence[typing.Type[_ModelSupportsSequence]]) -> bool | typing.NoReturn:
        async with self as conn:
            try:
                for idx, table in enumerate(tables):
                    self.log.warning(f"Creating table {table}...")
                    columns = [
                        f'{attr} {type_} {" ".join([
                            constraint for constraint in constraints
                        ])}' for attr, type_, constraints in [self._get_attr_type_constraints(arg, typ) for arg, typ in _models[idx].__sequence_fields__()]
                    ]
                    await conn.pool.execute(
                        f"""
                            CREATE TABLE IF NOT EXISTS {table} (
                                {", ".join(columns)}
                            );
                        """
                    )
                    self.log.warning(f"Created table {table}")
            except Exception as e:
                self.log.warning(f"Error creating table {table}...")
                raise e

    async def drop_tables(self, tables: typing.Sequence[str] | typing.Iterable[str]) -> None:
        async with self as conn:
            try:
                for table in tables:
                    self.log.warning(f"Dropping table {table}...")
                    await conn.pool.execute(
                        f"DROP TABLE IF EXISTS {table}"
                    )
                    self.log.warning(f"Dropped table {table}")
            except Exception as e:
                self.log.warning(f"Error dropping table {table}...")
                raise e

async def pool_getter() -> typing.AsyncGenerator[asyncpg.pool.Pool, None]:
    mgr = await AsyncPGPoolManager.get_instance()
    yield mgr.pool

async def mgr_getter() -> typing.AsyncGenerator[AsyncPGPoolManager, None]:
    mgr = await AsyncPGPoolManager.get_instance()
    yield mgr

class IDFactory:
    id: typing.ClassVar[int | None] = None

    @classmethod
    def get(cls) -> int:
        if cls.id is None:
            cls.id = 0
        cls.id += 1
        return cls.id

class AddTaskModel(_ModelSupportsSequence):
    id: int = Field(
        default_factory=IDFactory.get
    )
    title: str
    description: str
    done: bool = Field(
        default=False
    )
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4
    )

class _TaskDTO(typing.TypedDict):
    id: int
    title: str
    desc: str
    done: bool
    uid: uuid.UUID