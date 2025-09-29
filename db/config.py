import pathlib
import typing

class DBConfig:
    _extensions: typing.ClassVar[list[str]] = []
    _sql_dir: typing.ClassVar[pathlib.Path]

    @classmethod
    def set_sql_dir(cls, path: pathlib.Path) -> None:
        cls._sql_dir = path

    @classmethod
    def sql_dir(cls) -> pathlib.Path:
        return cls._sql_dir

    @classmethod
    def unset_sql_dir(cls) -> None:
        cls._sql_dir = None

    @classmethod
    def new_extension(cls, extension: str) -> None:
        cls._extensions.append(extension)

    @classmethod
    def extensions(cls) -> list[str]:
        return cls._extensions

    @classmethod
    def clear_extensions(cls) -> None:
        cls._extensions = []