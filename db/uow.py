import asyncpg
from db.manager import AsyncPGPoolManager
import typing

__all__ = (
    "AsyncPGPoolManager"
)

class UnitOfWork:
    __instance: typing.ClassVar["UnitOfWork | None"] = None

    def __init__(self) -> None:
        self.mgr: AsyncPGPoolManager | None = None
        self.conn: asyncpg.Connection | None = None
        self.transaction: typing.Any | None = None

    @classmethod
    def instance(cls) -> "UnitOfWork":
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance

    async def __aenter__(self) -> asyncpg.Connection:
        self.mgr = await AsyncPGPoolManager.instance()
        self.conn = await self.mgr.pool.acquire()
        self.transaction = self.conn.transaction()
        await self.transaction.__aenter__()
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.transaction:
            await self.transaction.__aexit__(exc_type, exc_val, exc_tb)
        if self.mgr and self.conn:
            await self.mgr.pool.release(self.conn)