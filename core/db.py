from typing import Generator

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from core import settings
from internal import models  # noqa # pylint: disable=unused-import

__all__ = ["engine", "get_db", "init_db"]

engine = create_engine(
    settings.database_url,
    echo=True,
    connect_args={"check_same_thread": False},
)


def get_db() -> Generator:
    with Session(engine) as session:
        yield session


def init_db(engine: Engine):
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
