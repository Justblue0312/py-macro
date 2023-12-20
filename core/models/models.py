from typing import Optional

from internal import SQLModelBase


class Blocks(SQLModelBase, table=True):
    __tablename__ = "blocks"  # type: ignore

    block_name: str
    block_description: Optional[str]


class BlockProcesses(SQLModelBase, table=True):
    __tablename__ = "block_processes"  # type: ignore

    block_id: str
    process_name: str
    process_time: str
    additional_data: Optional[str]


class MappingReport(SQLModelBase, table=True):
    __tablename__ = "mapping_report"  # type: ignore

    s_id: Optional[str]
    s_slug: Optional[str]
    t_id: Optional[str]
    t_slug: Optional[str]
    additional_data: Optional[str]
