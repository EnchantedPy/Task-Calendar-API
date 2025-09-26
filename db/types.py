import typing
from loguru import logger as log


class AbstractDBType:
    def __init__(
        self,
        index: bool = False,
        unique: bool = False,
        nullable: bool = False,
        default: str = None,
        pk: bool = False
    ) -> None:
        if pk:
            self._pk = True
            self._unique = True
            self._index = True
            self._nullable = False
            self._default = None
        else:
            self._pk = False
            self._index = index
            self._unique = unique
            self._nullable = nullable
            self._default = default

    def __pk__(self) -> bool:
        return self._pk

    def __index__(self) -> bool:
        return self._index

    def __unique__(self) -> bool:
        return self._unique

    def __nullable__(self) -> bool:
        return self._nullable

    def __default__(self) -> str:
        return self._default

    def __autoincrement__(self) -> bool:
        return getattr(self, "_autoincrement", False)

    def __init_subclass__(cls, **kwargs):
        def __construct_call__(subclass_name: str) -> typing.Callable[[typing.Self], str]:
            def __call__(self) -> str:
                return subclass_name
            return __call__

        cls.__call__ = __construct_call__(cls.__name__)


class String(AbstractDBType):
    pass


class Boolean(AbstractDBType):
    pass


class Integer(AbstractDBType):
    def __init__(
        self,
        index: bool = False,
        unique: bool = False,
        nullable: bool = False,
        default: typing.Any = None,
        pk: bool = False,
        autoincrement: bool = False
    ) -> None:
        self._autoincrement = autoincrement

        if autoincrement:
            pk = True
            default = None
            index = True
            unique = True
            nullable = False

        super().__init__(
            index=index,
            unique=unique,
            nullable=nullable,
            default=default,
            pk=pk
        )

    def __call__(self) -> str:
        if self._autoincrement:
            log.critical("Returned SERIAL")
            return "SERIAL"
        log.critical("Returned INTEGER")
        return "Integer"


class UUID(AbstractDBType):
    pass


class DateTime(AbstractDBType):
    pass
