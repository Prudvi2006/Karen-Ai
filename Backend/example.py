from pymongo import MongoClient

uri = "mongodb+srv://thallapallyprudviteja_db_user:Prudvi%402006@cluster0.fvqltmf.mongodb.net/?appName=Cluster0"

client = MongoClient(uri, serverSelectionTimeoutMS=5000)

try:
    print(client.admin.command("ping"))
except Exception as e:
    print(type(e))
    print(e)