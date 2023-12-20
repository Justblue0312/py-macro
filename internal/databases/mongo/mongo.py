from pymongo import MongoClient

from internal.databases.databases import DatabaseConfig, DatabaseInterface


class MongoConfig(DatabaseConfig):
    def __init__(self, database_uri: str, *args, **kwargs) -> None:
        self.database_uri = database_uri


class Mongo(DatabaseInterface):
    def __init__(self, config: MongoConfig) -> None:
        self.config = config
        self.client = MongoClient(self.config.database_uri)
