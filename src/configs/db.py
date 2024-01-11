from loguru import logger
from pymongo import MongoClient

from src.common import envs
from src.models.base import ConnectionMeta


class MainMongo:
    def __init__(self, **kwargs) -> None:
        self.metadata: ConnectionMeta = ConnectionMeta(
            host=envs.MONGO_HOST,
            port=envs.MONGO_PORT,
            database=envs.MONGO_DATABASE,
        )

        try:
            self.client: MongoClient = MongoClient(
                self.metadata.url(base="mongodb", with_db=False), **kwargs
            )
            self.conn = self.client[self.metadata.database]
        except:
            logger.warning("Fail connect to mongo")
            raise

    def close(self):
        self.client.close()
