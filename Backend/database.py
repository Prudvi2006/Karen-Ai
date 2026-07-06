# pyrefly: ignore [missing-import]
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["chatbot_db"]
chats_collection = db["chats"]
messages_collection = db["messages"]
users_collection = db["users"]

