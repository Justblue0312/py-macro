from typing import Optional
from sqlmodel import SQLModel, Field
import decimal
import datetime


class BlockProcesses(SQLModel, table=True):
	__table_name__ = "block_processes"

	index: Optional[int] = Field(primary_key=True)
	id: Optional[int] = Field(primary_key=True)
	created_at: datetime.datetime
	updated_at: datetime.datetime
	block_id: str
	process_name: str
	process_time: str
	additional_data: Optional[str] = None

class Blocks(SQLModel, table=True):
	__table_name__ = "blocks"

	index: Optional[int] = Field(primary_key=True)
	id: Optional[int] = Field(primary_key=True)
	created_at: datetime.datetime
	updated_at: datetime.datetime
	block_name: str
	block_description: Optional[str] = None

class Foo(SQLModel, table=True):
	__table_name__ = "foo"

	index: Optional[int] = Field(primary_key=True)
	id: Optional[int] = Field(primary_key=True)
	created_at: datetime.datetime
	updated_at: datetime.datetime
	bar: str

class MappingReport(SQLModel, table=True):
	__table_name__ = "mapping_report"

	index: Optional[int] = Field(primary_key=True)
	id: Optional[int] = Field(primary_key=True)
	created_at: datetime.datetime
	updated_at: datetime.datetime
	s_id: Optional[str] = None
	s_slug: Optional[str] = None
	t_id: Optional[str] = None
	t_slug: Optional[str] = None
	additional_data: Optional[str] = None

