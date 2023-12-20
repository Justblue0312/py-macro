import os
import time
from typing import Any, Generic, Literal, Optional

from contrib import BaseLogging, SQLModelGenerator
from core import SRC_DIR
from internal import Block, DBConfigType, DBInterfaceType, MySQL, PostgresSQL, SQLite

logger = BaseLogging("sql_block")


class SQLBlock(Block, Generic[DBConfigType, DBInterfaceType]):
    def __init__(
        self,
        data: Any,
        *,
        title: Optional[str] = "",
        description: Optional[str] = "",
        prefix: str = "",
        mode: Literal["start", "end", ""] = "",
        db_type: Literal["mysql", "sqlite", "postgres"] = "sqlite",
        config: DBConfigType,
        db: Optional[DBInterfaceType] = None,
        allow_process: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(
            data,  # type: ignore
            title=title,
            description=description,
            prefix=prefix,
            mode=mode,
            **kwargs,
        )
        self.config = config
        self.allow_process = allow_process
        self.db_type = db_type
        match self.db_type:
            case "sqlite":
                self.db = SQLite(config=self.config)  # type: ignore
            case "mysql":
                self.db = MySQL(config=self.config)  # type: ignore
            case "postgres":
                self.db = PostgresSQL(config=self.config)  # type: ignore
            case _:
                self.db = db
        if not self.db:
            raise ValueError("Can't establish database connection")
        if self.allow_process:
            self.preprocess()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.session.close()  # type: ignore
        self.db.engine.dispose()  # type: ignore

    def _check_python_file(self, filename: str):
        if filename.endswith(".py"):
            return filename
        else:
            return f"{filename}.py"

    def verify(self, *args, **kwargs) -> bool:
        return True if isinstance(self.data, dict) else False

    def preprocess(self, *args, **kwargs) -> bool:
        super().preprocess(*args, **kwargs)
        module = self.data.get("source_file")
        if not module:
            raise ValueError("Incorrect config format")
        file_path = os.path.join(SRC_DIR, self._check_python_file(module))
        try:
            s = SQLModelGenerator(file_path, self.db.engine, self.db.metadata)  # type: ignore
            self.generator = s
            s.generate()
        except Exception as e:
            logger.error(e)

        while not os.path.exists(file_path):
            time.sleep(1)
        if os.path.isfile(file_path):
            return True
        else:
            raise ValueError("%s isn't a file!" % file_path)

    def process(self, *args, **kwargs) -> Any | None:
        "Use with syntax instead due to the database connection."
        super().process(*args, **kwargs)
