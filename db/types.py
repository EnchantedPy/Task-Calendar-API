"""
Boolean, String, Integer, UUID, DateTime
"""

class _AbstractDBType:

    def __init_subclass__(cls, **kwargs):
        def __init__(self, index: bool = False) -> None:
            self.index = index

        def __call__(self) -> str:
            return self.__class__.__name__

        cls.__init__ = __init__
        cls.__call__ = __call__

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