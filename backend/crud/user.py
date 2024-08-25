from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
import bcrypt
from core.database import users

def get_user_by_username(username: str):
    try:
        return users.find_one({"username": username})
    except PyMongoError as e:
        raise Exception(f"Database error: {str(e)}")

def create_user(username: str, password: str):
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users.insert_one({"username": username, "password": hashed_password})
    except PyMongoError as e:
        raise Exception(f"Database error: {str(e)}")

def verify_password(stored_password: str, provided_password: str) -> bool:
    if isinstance(stored_password, str):
        stored_password = stored_password.encode('utf-8')
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)
