import textwrap

import aiofiles
import asyncpg
from db.models import BaseAbstractModel
from core.settings import settings
import typing
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
        if not cls.__instance:
            cls.__instance = cls()
        cls.__instance.pool = await cls.__instance.__create_connection_pool()
        return cls.__instance

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

    def _get_constraints_based_on_class_db_type(
            self,
            anno_cls_instance: types.AbstractDBType
    ) -> str:
        val = anno_cls_instance.__default__()

        if anno_cls_instance.__class__.__name__ == "String":
            default = f"DEFAULT '{val}'" if val else ""
        else:
            default = f"DEFAULT {val}" if val else ""

        parts = []
        if anno_cls_instance.__pk__():
            parts.append("PRIMARY KEY")
        if anno_cls_instance.__unique__():
            parts.append("UNIQUE")
        if not anno_cls_instance.__nullable__():
            parts.append("NOT NULL")
        if default:
            parts.append(default)

        query = " ".join(parts)
        return query

    def _get_columns_based_on_attrs_and_type_instances(
            self,
            _model: typing.Type[BaseAbstractModel]
    ) -> typing.Sequence[str]:
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
            returning.append(f"{column[0]} {conventions[column[1].__call__()]} {self._get_constraints_based_on_class_db_type(column[1])}") # may coz issues, change to .__call__()
        return returning

    async def create_tables(
            self,
            tables: typing.Sequence[str],
            _models: typing.Sequence[typing.Type[BaseAbstractModel]]
    ) -> None:
        self.log.warning(
            f"Creating tables {tables!r} using models {[model.__cls_repr__() for model in _models]}"
        )
        async with self as conn:
            try:
                for idx, table in enumerate(tables):
                    self.log.warning(f"Creating table {table}...")
                    columns = [
                        column for column in self._get_columns_based_on_attrs_and_type_instances(_models[idx])
                    ]
                    query = textwrap.dedent(
                        f"""
                            CREATE TABLE IF NOT EXISTS {table} (
                                {", ".join(columns)}
                            );
                        """
                    )
                    # self.log.critical(query)
                    async with aiofiles.open(DBConfig.sql_dir() / f"{table}_table_created.sql", "w") as file:
                        await file.write(query)
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
                    query = f"DROP TABLE IF EXISTS {table}"
                    async with aiofiles.open(DBConfig.sql_dir() / f"{table}_table_dropped.sql", "w") as file:
                        await file.write(query)
                    await conn.pool.execute(
                        query
                    )
                    self.log.warning(f"Dropped table {table}")
            except Exception as e:
                self.log.warning(f"Error dropping table {table}...")
                raise e

    async def run_pre_init_hook(self) -> None:
        async with self as conn:
            statements = []
            try:
                extensions = DBConfig.extensions()
                self.log.warning("Running pre-init hook...")
                for extension in extensions:
                    self.log.warning(
                        f"Creating extensions {extension!r}"
                    )
                    query = f"CREATE EXTENSION IF NOT EXISTS \"{extension}\";"
                    statements.append(query)
                    await conn.pool.execute(
                        query
                    )
                async with aiofiles.open(DBConfig.sql_dir() / "extensions_created.sql", "w") as file:
                    await file.write(
                        "\n".join(statements)
                    )
                log.warning("Pre init hook completed successfully")
            except Exception as e:
                log.warning(f"Pre init hook failed...")
                raise e

    async def run_post_init_hook(self, tables: list[str], _models: list[typing.Type[BaseAbstractModel]]) -> None:
        async with self as conn:
            try:
                log.warning("Running post init hook...")
                for table, model in zip(tables, _models):
                    indexes = model.__sequence_indexes__()

                    for index in indexes:
                        self.log.warning(
                            f"Creating index {index} in table {table}..."
                        )
                        stmt = f"CREATE INDEX {table}_{index}_index ON {table} ({index})"
                        async with aiofiles.open(DBConfig.sql_dir() / f"{table}_{index}_index_created.sql", "w") as file:
                            await file.write(stmt)
                        await conn.pool.execute(stmt)

                log.warning("Post init hook completed successfully")
            except Exception as e:
                log.warning(f"Post init hook failed...")
                raise e

    async def run_after_shutdown_hook(self) -> None:
        async with self as conn:
            statements = []
            try:
                extensions = DBConfig.extensions()
                for extension in extensions:
                    self.log.warning(
                        f"Dropping extension {extension!r}"
                    )
                    query = f"DROP EXTENSION IF EXISTS \"{extension}\";"
                    statements.append(query)
                    await conn.pool.execute(
                        query
                    )
                async with aiofiles.open(DBConfig.sql_dir() / f"extensions_dropped.sql", "w") as file:
                    await file.write(
                        "\n".join(statements)
                    )
                log.warning("After shutdown hook completed successfully")
            except Exception as e:
                log.warning(f"After shutdown hook failed...")
                raise e