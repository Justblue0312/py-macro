from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from internal.databases.databases import DatabaseConfig, DatabaseInterface


class MongoConfig(DatabaseConfig):
    def __init__(self, database_uri: str, *args, **kwargs) -> None:
        self.database_uri = database_uri


class Mongo(DatabaseInterface):
    def __init__(self, config: MongoConfig) -> None:
        self.config = config
        self.client = MongoClient(self.config.database_uri)

    def __enter__(self, *args, **kwargs) -> "Mongo":
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()

    def get_database(self, database_name: str) -> Database:
        return self.client.get_database(database_name)

    def get_connection(self, database: Database, collection_name: str) -> Collection:
        return database.get_collection(collection_name)
