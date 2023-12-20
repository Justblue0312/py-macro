from sqlmodel import select

from contrib import InitLogger
from core import env
from core.db import init_db, marco_engine
from internal import MySQLConfig, SQLiteConfig
from src.blocks import SQLBlock


def main():
    InitLogger()
    init_db(marco_engine)
    env.set("src", {"source_file": "src"})
    env.set("tar", {"source_file": "tar"})
    env.build()


if __name__ == "__main__":
    main()
    s_block = SQLBlock(
        data=env.get("src"),
        db_type="mysql",
        config=MySQLConfig(
            db_name="db_name",
            host="host",
            username="username",
            password="password",
        ),
        allow_process=True,
    )

    t_block = SQLBlock(
        data=env.get("tar"),
        db_type="sqlite",
        config=SQLiteConfig("sqlite_url"),
        allow_process=True,
    )

    with s_block as src, t_block as tar:
        try:
            import importlib

            src_model = importlib.import_module("src.src")
            tar.db.auto_migrate(src_model.ALL_TABLES)  # type:ignore
        except Exception as e:
            print(e)

        all_customers = src.db.session.exec(select(src_model.Customers))  # type:ignore
        for customer in all_customers:
            customer_data = customer.model_dump()
            if "id" in customer_data:
                del customer_data["id"]
            if "index" in customer_data:
                del customer_data["index"]
            print(customer_data)
            tar.db.session.add(src_model.Customers(**customer_data))  # type:ignore
        tar.db.session.commit()  # type:ignore
