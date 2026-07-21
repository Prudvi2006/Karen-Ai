# pyrefly: ignore [missing-import]
from pymongo import MongoClient
# from dotenv import load_dotenv
# import os
# load_dotenv()
# client = MongoClient(os.getenv("MONGODB_URI"))
# db = client["chatbot_db"]
# chats_collection = db["chats"]
# messages_collection = db["messages"]
# users_collection = db["users"]


from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("MONGODB_URI")

print("=" * 50)
print("Mongo URI:", uri)
print("=" * 50)

client = MongoClient(uri)

print(client.admin.command("ping"))

db = client["chatbot_db"]

users_collection = db["users"]
messages_collection = db["messages"]
chats_collection = db["chats"]