# pyrefly: ignore [missing-import]
import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Initialize MongoClient ONCE using the certifi CA bundle
client = MongoClient(
    os.getenv("MONGODB_URI"), 
    tlsCAFile=certifi.where()
)

# Reference your database and collections after client initialization
db = client["chatbot_db"]

chats_collection = db["chats"]
messages_collection = db["messages"]
users_collection = db["users"]