from typing import Literal

from sqlalchemy import URL

from internal.types.databases import DatabaseConfig, DatabaseInterface


class PostgresSQLConfig(DatabaseConfig):
    def __init__(
        self,
        username: str,
        password: str,
        db_name: str,
        host: str = "localhost",
        port: int = 5432,
        echo: bool = False,
        module: Literal["psycopg2", "pg8000"] | str = "psycopg2",
        *args,
        **kwargs,
    ) -> None:
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.db_name = db_name
        self.echo = echo
        self.module = module

        if not hasattr(self, "database_uri"):
            setattr(
                self,
                "database_uri",
                f"postgresql+{self.module}://{self.username}:{self.password}@{self.host}:{self.port}/{self.db_name}",
            )
        if kwargs.get("database_uri"):
            setattr(self, "database_uri", kwargs.get("database_uri"))
        if not self.database_uri:
            raise ValueError("Incorrect database_uri")

    @property
    def new_database_uri(self):
        return URL.create(
            "postgresql+psycopg2",
            self.username,
            self.password,
            self.host,
            self.port,
            self.db_name,
        )


class PostgresSQL(DatabaseInterface):
    def __init__(self, config: PostgresSQLConfig) -> None:
        super().__init__(config)
