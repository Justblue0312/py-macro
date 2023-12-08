from typing import TypeVar

from sqlmodel import SQLModel

BaseSQLModel = TypeVar("BaseSQLModel", bound=SQLModel)
