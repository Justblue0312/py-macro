from typing import Any, Dict, List, Optional

from sqlalchemy import text

from internal.databases.databases import DatabaseConfig, DatabaseInterface


class SQLiteConfig(DatabaseConfig):
    def __init__(
        self,
        database_uri: str,
        echo=False,
        connect_args: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs
    ) -> None:
        super().__init__(database_uri, echo, connect_args, *args, **kwargs)


class SQLite(DatabaseInterface):
    def __init__(self, config: SQLiteConfig) -> None:
        super().__init__(config=config)

    def show_tables(self) -> Optional[List[str]]:
        tables = self.session.exec(text("SELECT name FROM sqlite_master WHERE type = 'table';"))  # type: ignore
        return [table[0] for table in tables.fetchall()]
