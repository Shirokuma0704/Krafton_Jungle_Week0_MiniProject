import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_DB")

client = MongoClient(MONGO_URI)

db = client["pickme"]