import asyncpg
from models import BaseAbstractModel
from core.settings import settings
import typing
import uuid
from loguru import logger as log
from db.config import DBConfig
import db.types as types

class AsyncPGPoolManager:
    __instance: typing.ClassVar["AsyncPGPoolManager | None"] = None

    def __init__(self) -> None:
        self.pool: asyncpg.pool.Pool | None = None
        self.log = log

    @classmethod
    async def instance(cls) -> "AsyncPGPoolManager":
        if cls.__instance is None:
            cls.__instance = cls()
            cls.__instance.pool = await cls.__instance.__create_connection_pool()
        return cls.__instance

    @classmethod
    async def pool(cls) -> asyncpg.pool.Pool:
        return cls.__instance.pool

    @staticmethod
    async def __create_connection_pool() -> asyncpg.pool.Pool:
        pool = asyncpg.create_pool(
            user=settings.USER,
            password=settings.PASSWD,
            database=settings.DB,
            host=settings.HOST,
            port=settings.PORT,
            min_size=settings.MIN_POOL,
            max_size=settings.MAX_POOL,
        )
        return await pool

    async def __aenter__(self) -> typing.Self:
        self.pool = await self.__create_connection_pool()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self.pool = None

    @staticmethod
    def _get_constraints(arg) -> typing.Sequence[str]:
        constraints = []
        if arg == "uid":
            constraints.append("UNIQUE")
            constraints.append("NOT NULL")
            constraints.append("DEFAULT uuid_generate_v4()")
        if arg == "id":
            constraints.append("UNIQUE")
            constraints.append("NOT NULL")
        if arg == "date":
            constraints.append("NOT NULL")
            constraints.append("DEFAULT now()")
        if arg == "done":
            constraints.append("NOT NULL")
            constraints.append("DEFAULT false")
        return constraints

    def _get_attr_type_constraints(self, arg: str, typ: str) -> tuple[str, str, typing.Sequence[str]]:
        conventions: dict[str, str] = {
            "Integer": "INTEGER",
            "pk": "SERIAL PRIMARY KEY",
            "String": "TEXT",
            "Boolean": "BOOLEAN",
            "UUID": "UUID",
            "DateTime": "TIMESTAMPTZ"
        }
        type_ = "pk" if arg == "id" else typ
        self.log.warning(
            f"Current return expression: {arg, conventions[type_], self._get_constraints(arg)}"
        )
        return arg, conventions[type_], self._get_constraints(arg)

    def _get_constraints_based_on_class_db_type(
            self,
            anno_cls_instance: types.AbstractDBType
    ) -> str:
        val = anno_cls_instance.__default__()
        default = f"DEFAULT \"{val}\"" if val else ""
        query = f"{"SERIAL" if anno_cls_instance.__autoincrement__() else ""} {"PRIMARY KEY" if anno_cls_instance.__pk__() else ""} {"UNIQUE" if anno_cls_instance.__unique__() else ""} {"NOT NULL" if anno_cls_instance.__nullable__() else ""} {default}"
        self.log.critical(query)
        return query

    def _get_columns_based_on_attrs_and_type_instances(
            self,
            _model: typing.Type[BaseAbstractModel]
    ) -> typing.Sequence[str]:
        self.log.critical("Getting columns based on attrs and type")
        conventions: dict[str, str] = {
            "Integer": "INTEGER",
            "String": "TEXT",
            "Boolean": "BOOLEAN",
            "UUID": "UUID",
            "DateTime": "TIMESTAMPTZ",
            "SERIAL": "SERIAL"
        }
        returning = []
        columns: typing.Sequence[tuple[str, types.AbstractDBType]] = _model.__sequence_fields__()
        for column in columns:
            self.log.critical(f"Return type {column[1].__autoincrement__()}")
            returning.append(f"{column[0]} {conventions[column[1].__call__()]} {self._get_constraints_based_on_class_db_type(column[1])}") # may coz issues, change to .__call__()
        return returning

    async def create_tables(
            self,
            tables: typing.Sequence[str],
            _models: typing.Sequence[typing.Type[BaseAbstractModel]]
    ) -> None:
        async with self as conn:
            self.log.critical(
                "Create tables hook triggered"
            )
            self.log.critical(
                f"{tables} {_models}"
            )
            try:
                for idx, table in enumerate(tables):
                    self.log.critical(
                        "Inside for TABLE loop"
                    )
                    self.log.warning(f"Creating table {table}...")
                    columns = [
                        column for column in self._get_columns_based_on_attrs_and_type_instances(_models[idx])
                    ]
                    # columns = [
                    #     f'{attr} {type_} {" ".join([
                    #         constraint for constraint in constraints
                    #     ])}' for attr, type_, constraints in [self._get_attr_type_constraints(arg, typ) for arg, typ in _models[idx].__sequence_fields__()]
                    # ]
                    self.log.warning(columns)
                    query = (
                        f"""
                            CREATE TABLE IF NOT EXISTS {table} (
                                {", ".join(columns)}
                            );
                        """
                    )
                    self.log.critical(query)
                    await conn.pool.execute(
                        query
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

    async def run_pre_init_hook(self) -> None:
        async with self as conn:
            try:
                for extension in DBConfig.extensions():
                    await conn.pool.execute(
                        f"CREATE EXTENSION IF NOT EXISTS \"{extension}\";"
                    )
                log.warning("Pre init hook completed successfully")
            except Exception as e:
                log.warning(f"Pre init hook failed {self}...")
                raise e

    async def run_post_init_hook(self, tables: list[str], _models: list[typing.Type[BaseAbstractModel]]) -> None:
        async with self as conn:
            try:
                log.critical("Running post init hook")
                for table, model in zip(tables, _models):
                    self.log.warning(f"Running post init hook for table {table}...")
                    indexes = model.__sequence_indexes__()

                    for index in indexes:
                        self.log.critical("Inside index loop")
                        self.log.critical(f"Got index field - {index}")
                        stmt = f"CREATE INDEX {table}_{index}_index ON {table} ({index})"
                        self.log.info(f"Index statement - {stmt}")
                        await conn.pool.execute(stmt)

                    # for index in _models[i].__sequence_indexes__():
                    #     await conn.pool.execute(
                    #         f"CREATE INDEX {index}_index ON {table} ({index})"
                    #     )
                    #     i += 1
                log.warning("Post init hook completed successfully")
            except Exception as e:
                log.warning(f"Post init hook failed {self}...")
                raise e

    async def run_after_shutdown_hook(self) -> None:
        async with self as conn:
            try:
                for extension in DBConfig.extensions():
                    await conn.pool.execute(
                        f"DROP EXTENSION IF EXISTS \"{extension}\";"
                    )
                log.warning("After shutdown hook completed successfully")
            except Exception as e:
                log.warning(f"After shutdown hook failed {self}...")
                raise e

class _TaskDTO(typing.TypedDict):
    id: int
    title: str
    description: str
    done: bool
    uid: uuid.UUID