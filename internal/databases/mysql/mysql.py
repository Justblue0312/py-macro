import importlib
from typing import List, Literal, Optional

from sqlalchemy import URL, text

from internal.databases.databases import DatabaseConfig, DatabaseInterface


class MySQLConfig(DatabaseConfig):
    def __init__(
        self,
        username: str,
        password: str,
        db_name: str,
        host: str = "127.0.0.1",
        port: int = 3306,
        echo: bool = False,
        module: Literal["pymysql", "mysqlconnector"] | str = "pymysql",
        *args,
        **kwargs,
    ):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.db_name = db_name
        self.echo = echo
        self.module = module

        if self.module and self.module != "pymysql":
            try:
                importlib.import_module(self.module)
            except ImportError:
                raise ImportError(
                    f"Driver requires module {self.module} but not found."
                )

        if not hasattr(self, "database_uri"):
            setattr(
                self,
                "database_uri",
                f"mysql+{self.module}://{self.username}:{self.password}@{self.host}:{self.port}/{self.db_name}",
            )
        if kwargs.get("database_uri"):
            setattr(self, "database_uri", kwargs.get("database_uri"))
        if not self.database_uri:
            raise ValueError("Incorrect database_uri")

    @property
    def database_url(self):
        return URL.create(
            "mysql+pymysql",
            self.username,
            self.password,
            self.host,
            self.port,
            self.db_name,
        )


class MySQL(DatabaseInterface):
    def __init__(self, config: MySQLConfig) -> None:
        super().__init__(config=config)

    def show_tables(self) -> Optional[List[str]]:
        tables = self.session.exec(text("SHOW TABLES;"))  # type: ignore
        return [table[0] for table in tables.fetchall()]
