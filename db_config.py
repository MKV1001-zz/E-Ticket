import pymongo
from pymongo import MongoClient
import certifi
import ssl 



CONN_STRING ="mongodb+srv://mkv1001:vemms2001@cluster0.wbgpf.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

def conn():
    try:
        cluster = MongoClient(CONN_STRING, tlsCAFile=certifi.where())
        db = cluster.get_database('E-ticketing')
        print("connected")
        return db
    except Exception as e:
        raise Exception(e)
    
db = conn()
