from typing import Any, Dict, List, Optional

from sqlalchemy import text

from contrib import BaseLogging
from internal.types.databases import DatabaseConfig, DatabaseInterface

logger = BaseLogging("sqlite_error")


class SQLiteConfig(DatabaseConfig):
    def __init__(
        self,
        database_uri: str,
        echo=False,
        connect_args: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.database_uri = database_uri
        self.echo = echo
        self.connect_args = (
            connect_args if connect_args else {"check_same_thread": False}
        )


class SQLite(DatabaseInterface):
    def __init__(self, config: SQLiteConfig) -> None:
        super().__init__(config=config)

    def show_tables(self) -> Optional[List[str]]:
        tables = self.session.exec(text("SELECT name FROM sqlite_master WHERE type = 'table';"))  # type: ignore
        return [table[0] for table in tables.fetchall()]
