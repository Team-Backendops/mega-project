from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from core.config import settings

class MongoDBClient:
    _client = None
    _db = None
    _fs = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = AsyncIOMotorClient(settings.mongo_url)
        return cls._client

    @classmethod
    def get_db(cls):
        if cls._db is None:
            cls._db = cls.get_client()[settings.database_name]
        return cls._db

    @classmethod
    def get_gridfs(cls):
        if cls._fs is None:
            cls._fs = AsyncIOMotorGridFSBucket(cls.get_db())
        return cls._fs

service_collection = MongoDBClient.get_db()['business']
users = MongoDBClient.get_db()['users']
fs = MongoDBClient.get_gridfs()
