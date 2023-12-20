from typing import Generator

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from core import settings
from core.models import models  # noqa # pylint: disable=unused-import

__all__ = ["marco_engine", "get_db", "init_db"]

marco_engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False},
)


def get_db() -> Generator:
    with Session(marco_engine) as session:
        yield session


def init_db(engine: Engine):
    SQLModel.metadata.drop_all(marco_engine)
    SQLModel.metadata.create_all(marco_engine)
