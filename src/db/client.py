import os
import pymongo
from dotenv import load_dotenv
from pymongo import AsyncMongoClient

load_dotenv()


client = AsyncMongoClient(os.getenv("MONGO_URI"), server_api=pymongo.server_api.ServerApi(
    version="1", strict=True, deprecation_errors=True))
db = client["todo"]
