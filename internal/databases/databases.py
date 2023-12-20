import logging
from contextlib import contextmanager
from typing import Generator, Generic, List, TypeVar

from sqlalchemy.engine import Engine
from sqlmodel import MetaData, Session, create_engine

from internal.types.base import BaseSQLModel

DBConfigType = TypeVar("DBConfigType", bound="DatabaseConfig")
DBInterfaceType = TypeVar("DBInterfaceType", bound="DatabaseInterface")
logger = logging.getLogger(__name__)


class DatabaseConfig:
    def __init__(self, database_uri: str, echo: bool = False, *args, **kwargs) -> None:
        self.database_uri: str = database_uri
        self.echo = echo
        self.connect_args = kwargs.get("connect_args", None)


class DatabaseInterface(Generic[DBConfigType]):
    def __init__(self, config: DBConfigType) -> None:
        self.config: DBConfigType = config
        self.engine: Engine = create_engine(
            self.config.database_uri,
            echo=self.config.echo,
        )
        self.session: Session = Session(self.engine)
        self.metadata = MetaData()

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        if not self.session:
            self.session = Session(self.engine)
        try:
            yield self.session
            self.session.commit()
        except Exception as e:
            logger.error("Database error: %s " % e)
            self.session.rollback()
            raise
        finally:
            self.session.close()

    def __enter__(self, *args, **kwargs) -> "DatabaseInterface":
        return self

    def __exit__(self, exc_type, exc_value, traceback, *args, **kwargs):
        if self.session:
            self.session.close()

        if self.engine:
            self.engine.dispose()

    def auto_migrate(self, models: List[BaseSQLModel] | BaseSQLModel):
        if isinstance(models, list):
            for model in models:
                model.__table__.create(self.engine)
        else:
            models.__table__.create(self.engine)

    def drop_tables(self, models: List[BaseSQLModel] | BaseSQLModel):
        if isinstance(models, list):
            for model in models:
                model.__table__.drop(self.engine)
        else:
            models.__table__.drop(self.engine)
