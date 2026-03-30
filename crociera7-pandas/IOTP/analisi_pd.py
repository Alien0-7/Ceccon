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

## Creo il DataFrame
dataFrame = pd.DataFrame(risultato)

if  dataFrame.empty: 
    print("Non ci sono dati")
    exit(1)

# Printo le colonne 
#print(dataFrame.columns)

# Controllo che i dati siano numeri
dataFrame["temperatura"] = pd.to_numeric(dataFrame["temperatura"], errors="coerce")
dataFrame["umidita"] = pd.to_numeric(dataFrame["umidita"], errors="coerce")

# Calcolo media
media_temperatura = round(dataFrame["temperatura"].mean() , 2)
media_umidita = round(dataFrame["umidita"].mean() , 2)

# Calcolo della deviazione standard 
deviazione_temperatura = round(dataFrame["temperatura"].std() , 2)
deviazione_umidita = round(dataFrame["umidita"].std() , 2)

print("--- ANALISI DATI ---")
print("Numero di righe e colonne: ", dataFrame.shape , "\n")
print("Media temperatura:", media_temperatura)
print("Media umidità:", media_umidita)
print("Deviazione standard temperatura:", deviazione_temperatura)
print("Deviazione standard umidità:", deviazione_umidita)
