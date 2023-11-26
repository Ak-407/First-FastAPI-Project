from pymongo import MongoClient
MONGO_URI = "mongodb+srv://jsamaan:amaan123@cluster0.vz55wc0.mongodb.net/jsamaan?retryWrites=true&w=majority"
conn = MongoClient(MONGO_URI, tls=True,tlsAllowInvalidCertificates=True)

db = conn["jsamaan"]

new_users_collection = db["newUsers"]
notes_collection = db["notes"]