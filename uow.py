import asyncpg

from database import AsyncPGPoolManager
import typing
from loguru import logger as log

# class UnitOfWork:
#     __instance: typing.ClassVar["UnitOfWork | None"] = None
#
#     def __init__(self) -> None:
#         self.pool_mgr: typing.Type[AsyncPGPoolManager] | None = AsyncPGPoolManager
#         self.transaction = None
#         self.conn = None
#         self.log = log
#
#     @classmethod
#     async def get_instance(cls) -> "UnitOfWork":
#         if not cls.__instance:
#             cls.__instance = cls()
#         return cls.__instance
#
#     async def __aenter__(self) -> AsyncPGPoolManager:
#         __instance = await self.pool_mgr.get_instance()
#         __conn = await __instance.__aenter__()
#         __ts = await __conn.__aenter__()
#         self.conn = __conn
#         self.transaction = __ts
#         return __ts
#         # async with __instance.pool as pool:
#         #     async with pool.acquire() as conn:
#         #         async with conn.transaction() as ts:
#         #             self.transaction = ts
#         #             self.log.warning(type(self.transaction))
#         #             self.log.warning(type(ts))
#         #             return self
#
#     async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
#         await self.transaction.__aexit__(exc_type, exc_val, exc_tb)
#         await self.conn.__aexit__(exc_type, exc_val, exc_tb)

class UnitOfWork:
    __instance: typing.ClassVar["UnitOfWork | None"] = None

    def __init__(self) -> None:
        self.pool_mgr: AsyncPGPoolManager | None = None
        self.conn: asyncpg.Connection | None = None
        self.transaction: typing.Any | None = None

    @classmethod
    async def get_instance(cls) -> "UnitOfWork":
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance

    async def __aenter__(self) -> asyncpg.Connection:
        self.pool_mgr = await AsyncPGPoolManager.get_instance()
        self.conn = await self.pool_mgr.pool.acquire()
        self.transaction = self.conn.transaction()
        await self.transaction.__aenter__()
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.transaction:
            await self.transaction.__aexit__(exc_type, exc_val, exc_tb)
        if self.pool_mgr and self.conn:
            await self.pool_mgr.pool.release(self.conn)


async def get_uow() -> typing.AsyncGenerator[UnitOfWork, None]:
    uow = await UnitOfWork.get_instance()
    yield uow