"""
Boolean, String, Integer, UUID, DateTime
"""
import typing

class AbstractDBType:

    def __init__(
            self,
            index: bool = False,
            unique: bool = False,
            nullable: bool = False,
            default: str = False,
            pk: bool = False
    ) -> None:
        if pk:
            self.__pk = pk
            self.__unique = True
            self.__index = True
            self.__nullable = False
        else:
            self.__index = index
            self.__unique = unique
            self.__nullable = nullable
            self.__default = default

    def __autoincrement__(self) -> bool:
        return getattr(self, '__autoincrement', False)

    def __default__(self) -> str:
        return self.__default

    def __pk__(self) -> bool:
        return self.__pk

    def __index__(self) -> bool:
        return self.__index

    def __unique__(self) -> bool:
        return self.__unique

    def __nullable__(self) -> bool:
        return self.__nullable

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
            default: str = False,
            pk: bool = False,
            autoincrement: bool = False
    ) -> None:
        if autoincrement:
            self.__autoincrement = True
            self.__pk = True
            self.__unique = True
            self.__index = True
            self.__nullable = True
        elif pk and not autoincrement:
            self.__pk = pk
            self.__unique = True
            self.__index = True
            self.__nullable = False
            self.__autoincrement = False
        else:
            self.__index = index
            self.__unique = unique
            self.__nullable = nullable
            self.__default = default
            self.__autoincrement = False

        super().__init__(
            index=index,
            unique=unique,
            nullable=nullable,
            default=default,
            pk=pk
        )

class UUID(AbstractDBType):
    pass

class DateTime(AbstractDBType):
    pass