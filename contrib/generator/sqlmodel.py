from __future__ import annotations

import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union

import sqlalchemy
from slugify import slugify
from sqlmodel import Table

_CONVERT_DATA = {
    "int": [
        sqlalchemy.types.INTEGER,
        sqlalchemy.types.BIGINT,
        sqlalchemy.types.SMALLINT,
        sqlalchemy.types.Integer,
        sqlalchemy.types.SmallInteger,
        sqlalchemy.types.BigInteger,
    ],
    "str": [
        sqlalchemy.types.CHAR,
        sqlalchemy.types.VARCHAR,
        sqlalchemy.types.NCHAR,
        sqlalchemy.types.NVARCHAR,
        sqlalchemy.types.TEXT,
        sqlalchemy.types.Text,
        sqlalchemy.types.CLOB,
        sqlalchemy.types.String,
        sqlalchemy.types.Unicode,
        sqlalchemy.types.UnicodeText,
        sqlalchemy.types.Enum,
    ],
    "float": [
        sqlalchemy.types.FLOAT,
        sqlalchemy.types.REAL,
        sqlalchemy.types.Float,
    ],
    "decimal.Decimal": [
        sqlalchemy.types.NUMERIC,
        sqlalchemy.types.DECIMAL,
        sqlalchemy.types.Numeric,
    ],
    "datetime.datetime": [
        sqlalchemy.types.TIMESTAMP,
        sqlalchemy.types.DATETIME,
        sqlalchemy.types.DateTime,
    ],
    "bytes": [
        sqlalchemy.types.BLOB,
        sqlalchemy.types.BINARY,
        sqlalchemy.types.VARBINARY,
        sqlalchemy.types.LargeBinary,
        sqlalchemy.types._Binary,
    ],
    "bool": [sqlalchemy.types.BOOLEAN, sqlalchemy.types.Boolean],
    "datetime.date": [sqlalchemy.types.DATE, sqlalchemy.types.Date],
    "datetime.time": [sqlalchemy.types.TIME, sqlalchemy.types.Time],
    "datetime.timedelta": [sqlalchemy.types.Interval],
    "list": [sqlalchemy.types.ARRAY],
    "dict": [sqlalchemy.types.JSON],
    "uuid": [uuid.UUID],
}

# fmt: off
def convert(datatype: type) -> str:
    return next(pytype for pytype, sqltypes in _CONVERT_DATA.items() if any(isinstance(datatype, sqltype) for sqltype in sqltypes)
    )

# fmt: off
def convert_table_name(name: str) -> str:
    return "".join(item.capitalize() for item in slugify(name).replace("-", "_").split("_"))


def convert_column_name(name: str):
    return "_metadata" if name == "metadata" else slugify(name).replace("-", "_")


@dataclass
class ColumnD:
    name: str
    column_type: Union[str, Any]
    primary_key: bool = False
    nullable: bool = True


@dataclass
class TableD:
    name: str
    columns: Optional[List[ColumnD]] = field(default_factory=list)


# fmt: off
@dataclass
class SQLModelGenerator:
    outfile: str
    engine: sqlalchemy.Engine
    metadata: sqlalchemy.MetaData

    _imports: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    _module_imports: Set[str] = field(default_factory=set)

    def __post_init__(self):
        self.metadata.reflect(self.engine)
        self.tables: List[Table] = self.metadata.sorted_tables

    def add_import(self, pkgname: str, name: str | List[str]) -> None:
        names = self._imports.setdefault(pkgname, set())
        if isinstance(name, str):
            names.add(name)
        elif isinstance(name, list):
            names.update(set(name))

    def add_module_import(self, pkgname: str) -> None:
        self._module_imports.add(pkgname)

    def generate_model(self, table: Table) -> TableD:
        default_primary_key = ColumnD(name="index", column_type="int", primary_key=True, nullable=True)
        table_d_columns = [default_primary_key] if not any([col.type for col in table.columns]) else []
        table_d_columns += [ColumnD(convert_column_name(col.name), convert(col.type), col.primary_key, col.nullable) for col in table.columns] #type: ignore
        return TableD(name=table.name, columns=table_d_columns)

    def generate_sqlmodel(self, table_d: TableD) -> str:
        self.add_import("typing", "Optional")
        self.add_import("sqlmodel", ["SQLModel", "Field"])
        self.add_module_import("datetime") 
        self.add_module_import("decimal")  

        class_definition = f"class {convert_table_name(table_d.name)}(SQLModel, table=True):\n"
        class_definition += f'\t__table_name__ = "{table_d.name}"\n\n'
        for column in table_d.columns: #type: ignore
            if column.primary_key:
                class_definition += f"\t{column.name}: Optional[{column.column_type}] = Field(primary_key=True)\n"
            elif column.nullable:
                class_definition += f"\t{column.name}: Optional[{column.column_type}] = None\n"
            else:
                class_definition += f"\t{column.name}: {column.column_type}\n"
        class_definition += "\n"
        return class_definition

    def generate(self):
        all_data = "\n" + "".join(self.generate_sqlmodel(self.generate_model(table)) for table in self.metadata.sorted_tables)

        import_data = "".join(f"from {pkgname} import {', '.join(name)}\n" for pkgname, name in self._imports.items())
        import_data += "".join(f"import {name}\n" for name in self._module_imports)

        with open(self.outfile, mode="w", encoding="utf-8") as file:
            file.write(import_data + "\n" + all_data)

    @property
    def table_names(self) -> List[str]:
        return [convert_table_name(table.name) for table in self.tables]
