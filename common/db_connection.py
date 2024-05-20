from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


# DATABASE_NAME = "logs"
# URI = "mongodb+srv://ngduclong173:lRTTd7JxwBgEVO0W@cluster0.tva8uce.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# def connect_to_db():
#   # Create a new client and connect to the server
#   # client = MongoClient(uri, server_api=ServerApi('1'))
  
#   client = MongoClient("mongodb://localhost:27017/")

#   # Send a ping to confirm a successful connection
#   try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
#   except Exception as e:
#     print(e)

#   # Return connection instance
#   return client[DATABASE_NAME]


DATABASE_NAME = "logs"
CLOUD_URI = "mongodb+srv://ngduclong173:lRTTd7JxwBgEVO0W@cluster0.tva8uce.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
LOCAL_URI = "mongodb://localhost:27017/"

def connect_to_db(cloud=False):
    # Determine URI based on the parameter
    uri = CLOUD_URI if cloud else LOCAL_URI
    print(uri)
    # Create a new client and connect to the server
    if cloud:
      client = MongoClient(uri, server_api=ServerApi('1'))
    else: 
      client = MongoClient(uri)

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        return e
    # Return connection instance
    return client[DATABASE_NAME]