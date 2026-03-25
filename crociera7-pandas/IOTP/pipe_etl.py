'''
Allegro Elena, Morari Elia 
5AI

Script pipe_eyl.py (filtraggio dei dati)
'''
import time 
import json 
import random 
import pymongo 
from datetime import datetime 
import pandas as pd 
from pandas import json_normalize

file_mongo = open("mongo.conf")
dict_mongo = json.load(file_mongo)

client = pymongo.MongoClient(dict_mongo["uri_pulire"])
db_pulire = client[dict_mongo["database_pulire"]]
mycol = db_pulire[dict_mongo["collezione_pulire"]]

# Connessione al database "nave"
col_nave = db_pulire["misurePuliteAllegro"]

risultato = list(mycol.find())
print(risultato)

# dataFrame = json_normalize(risultato)
dataFrame = pd.DataFrame(risultato)

if not dataFrame.empty: 
    print("Dati caricati")
else: 
    exit(1)

# Rinomino le colonne 
dataFrame = dataFrame.rename(columns= {'temperaturam': 'temperatura'})
dataFrame = dataFrame.rename(columns= {'umiditam': 'umidita'})

# Conversione colonna della data e ora in datetime 
dataFrame['dataeora'] = pd.to_datetime(dataFrame['dataeora'], unit= 's')

# Controllo delle temperature e dell'umidità
df_filtrato = dataFrame[(dataFrame['temperatura'].between(18, 26)) & (dataFrame['umidita'].between(40, 60))]
df_filtrato = df_filtrato.sort_values(by= "cabina", ascending= True)
df_filtrato = df_filtrato.drop(columns=['_id'])
# Converto il DataFrame in dizionario
records = df_filtrato.to_dict(orient="records")

# Inserisco i dati
if records:
    col_nave.insert_many(records)
    print("Dati inseriti nella collezione misurePulite")
else:
    print("Nessun dato da inserire")