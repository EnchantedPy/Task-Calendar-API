import typing

class DBConfig:
         _extensions: typing.ClassVar[list[str]] = []

         @classmethod
         def new_extension(cls, extension: str) -> None:
             cls._extensions.append(extension)

         @classmethod
         def extensions(cls) -> list[str]:
             return cls._extensions