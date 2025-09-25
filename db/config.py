import typing

class DBConfig:
         __extensions: typing.ClassVar[list[str]]

         @classmethod
         def new_extension(cls, extension: str) -> None:
             cls.__extensions.append(extension)

         @classmethod
         def extensions(cls) -> list[str]:
             return cls.__extensions