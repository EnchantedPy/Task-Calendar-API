from db.manager import AsyncPGPoolManager
from models import BaseAbstractModel
from db.config import DBConfig

__all__ = (
    "ASGILifespan"
)

class ASGILifespan:

    @staticmethod
    async def startup() -> None:
        DBConfig.new_extension(
            "uuid-ossp"
        )

        mgr = await AsyncPGPoolManager.instance()

        # Pre init hook
        await mgr.run_pre_init_hook()

        # Tables creation
        await mgr.create_tables(
            tables=BaseAbstractModel.tables(),
            _models=BaseAbstractModel.models()
        )

        # Post init hook
        await mgr.run_post_init_hook(
            tables=BaseAbstractModel.tables(),
            _models=BaseAbstractModel.models()
        )

    @staticmethod
    async def shutdown() -> None:
        mgr = await AsyncPGPoolManager.instance()

        # Tables dropping
        await mgr.drop_tables(
            tables=BaseAbstractModel.tables()
        )

        # After shutdown hook
        await mgr.run_after_shutdown_hook()