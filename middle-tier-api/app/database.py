from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()  # will load .env in this folder

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "syllabus_sync")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

syllabi_collection = db["syllabi"]
tasks_collection = db["tasks"]
