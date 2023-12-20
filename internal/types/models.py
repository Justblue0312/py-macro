from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from internal.types.mixin import ActiveRecordMixin


class SQLModelBase(SQLModel):
    id: Optional[int] = Field(default_factory=int, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SQLModelMixin(SQLModel, ActiveRecordMixin):
    pass
