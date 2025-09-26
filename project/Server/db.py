from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "crop_app_db")

_client = MongoClient(MONGO_URI)
_db = _client[MONGO_DB]

def get_db():
    """
    Returns the MongoDB database instance.
    """
    return _db
