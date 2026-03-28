'''
Allegro Elena, Morari Elia 
5AI

Script analisi_pd.py (calcolo media e deviazione standard)
'''
import json
import pymongo
import math
import pandas as pd

# Apro il file per la connessione a Mongo
file_mongo = open("mongo.conf")
dict_mongo = json.load(file_mongo)

client = pymongo.MongoClient(dict_mongo["uri"])
db = client[dict_mongo["database"]]

# Connessione al database
mycol = db[dict_mongo["collezione"]] # collezione: misurepuliteALLEGRO

risultato = list(mycol.find())
print(risultato)
