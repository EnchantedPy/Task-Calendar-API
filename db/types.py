"""
Boolean, String, Integer, UUID, DateTime
"""
from loguru import logger as log
import typing

class _AbstractDBType:

    def __init_subclass__(cls, **kwargs):

        def __construct_init__() -> typing.Callable[[typing.Self, bool], None]:
            def __init__(self, index: bool = False) -> None:
                self.index = index
                # add Unique, Nullable
            return __init__

        def __construct_call__(subclass_name: str) -> typing.Callable[[typing.Self], str]:
            def __call__(self) -> str:
                log.warning(
                    f"Returned {subclass_name} out of __call__"
                )
                return subclass_name
            return __call__

        def __index__(self) -> bool:
            return self.index

        cls.__init__ = __construct_init__()
        cls.__index__ = __index__
        cls.__call__ = __construct_call__(cls.__name__)

class String(_AbstractDBType):
    pass

class Boolean(_AbstractDBType):
    pass

class Integer(_AbstractDBType):
    pass

class UUID(_AbstractDBType):
    pass

class DateTime(_AbstractDBType):
    pass