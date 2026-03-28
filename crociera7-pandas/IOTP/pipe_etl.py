'''
Allegro Elena, Morari Elia 
5AI

Script pipe_eyl.py (filtraggio dei dati)
''' 
import json 
import pymongo 
from datetime import datetime 
import pandas as pd 

# Apro il file per la connessione a Mongo
file_mongo = open("mongo.conf")
dict_mongo = json.load(file_mongo)

client = pymongo.MongoClient(dict_mongo["uri"])
db_pulire = client[dict_mongo["database"]]

# Connessione al database "Navi"
mycol = db_pulire[dict_mongo["collezione_pulire"]] # collezione: misure
col_nave = db_pulire[dict_mongo["collezione"]] # collezione: misurepuliteALLEGRO

risultato = list(mycol.find())
print(risultato)

# dataFrame = json_normalize(risultato)
dataFrame = pd.DataFrame(risultato)

# Controllo se il DataFrame è vuoto
if not dataFrame.empty: 
    print("Dati caricati")
else: 
    print("Non ci sono dati da caricare ")
    exit(1)

# Rinomino le colonne 
dataFrame = dataFrame.rename(columns= {'temperaturam': 'temperatura', 
                                      'umiditam': 'umidita' })
#dataFrame = dataFrame.rename(columns= {'umiditam': 'umidita'})

# Conversione colonna della data e ora in datetime 
dataFrame['dataeora'] = pd.to_datetime(dataFrame['dataeora'], unit= 's')

# Controllo delle temperature e dell'umidità
df_filtrato = dataFrame[
    (dataFrame['temperatura'].between(18, 26)) &
    (dataFrame['umidita'].between(40, 60))
]

# Ordino i dati in base alla cabina
df_filtrato = df_filtrato.sort_values(by= "cabina", ascending= True)
# Rimuovo la colonna "_id"
df_filtrato = df_filtrato.drop(columns=['_id'])

# Converto il DataFrame in dizionario
dati = df_filtrato.to_dict(orient="records")

# Inserisco i dati nella nuova collezione
if dati:
    col_nave.insert_many(dati)
    print("Dati inseriti nella collezione misurepuliteALLEGRO")
else:
    print("Nessun dato da inserire")