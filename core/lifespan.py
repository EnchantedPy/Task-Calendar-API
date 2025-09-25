from database import AsyncPGPoolManager
import models

__all__ = (
    "ASGILifespan"
)

class ASGILifespan:

    @staticmethod
    async def startup() -> None:
        mgr = await AsyncPGPoolManager.instance()
        await mgr.run_pre_init_hook()
        await mgr.create_tables(
            tables=["tasks", "calendar_notes"],
            _models=[models._TaskModel, models._CalendarNoteModel]
        )
        await mgr.run_post_init_hook(
            tables=["tasks", "calendar_notes"],
            _models=[models._TaskModel, models._CalendarNoteModel]
        )

    @staticmethod
    async def shutdown() -> None:
        mgr = await AsyncPGPoolManager.instance()
        await mgr.drop_tables(
            tables=["tasks", "calendar_notes"],
        )
        await mgr.run_after_shutdown_hook()