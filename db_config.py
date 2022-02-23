import pymongo
from pymongo import MongoClient
import certifi
import os


user = os.environ.get("MONGO_USER")
password= os.environ.get("MONGO_PASS")
CONN_STRING =f"mongodb+srv://{user}:{password}@cluster0.wbgpf.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

def conn():
    try:
        cluster = MongoClient(CONN_STRING, tlsCAFile=certifi.where())
        db = cluster.get_database('E-ticketing')
        print("connected")
        return db
    except Exception as e:
        raise Exception(e)
    

