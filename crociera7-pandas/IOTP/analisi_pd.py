'''
Allegro Elena, Morari Elia 
5AI

Script analisi_pd.py (calcolo media e deviazione standard)
'''
import json
import pymongo
import math
import pandas as pd

file = open("mongo.conf") 
dict = json.load(file)

# Prendo dal file di configurazione i parametri 
uri = dict['uri']
db_name = dict['database']
collezione = dict['collezione']

client = pymongo.MongoClient(uri)

db = client["Nave2025"] # Nome Database 
collezione = db["misure"] # Collezione 

# Risultato della query 
risultato = list(collezione.find())
print(risultato)

# dataFrame = json_normalize(risultato)
dataFrame = pd.DataFrame(risultato)

print("Analisi dei dati: ")
temperatura = dataFrame["temperaturam"].mean()
print("Temperatura:", temperatura)

umidita = dataFrame["umiditam"].mean()
print("Umidità:",umidita)

deviazione_s = dataFrame["temperaturam"].std()
print("Temperatura:",umidita)

deviazione_s = dataFrame["umiditam"].std()
print("Temperatura:",umidita)


if (risultato):
    print("[DEBUG] Documenti trovati:")
    lista_documenti = list(risultato) # Converti il cursore in una lista per poterlo iterare più volte
    
    n_valori = len(lista_documenti)
    print(f"Numero di misurazioni trovate: {n_valori}")

    media_temp = 0.0
    media_umid = 0.0
    # Prendo i dati della temperatura e dell'umidità
    for documento in lista_documenti:
        media_temp += documento["temperaturam"]
        media_umid += documento["umiditam"]
    
    # Calcolo le varie medie 
    media_temp /= n_valori
    media_umid /= n_valori

    print(f"Media temperatura: {media_temp} °C")
    print(f"Media umidità: {media_umid} %")

    somma_quadrati_temp = 0.0
    somma_quadrati_umid = 0.0

    # Faccio la deviazione standard dei dati della temperatura e dell'umidità
    for documento in lista_documenti:
        somma_quadrati_temp += (documento["temperaturam"] - media_temp) ** 2
        somma_quadrati_umid += (documento["umiditam"] - media_umid) ** 2
    
    if n_valori > 1:
        deviazione_temp = math.sqrt(somma_quadrati_temp / (n_valori - 1))
        deviazione_umid = math.sqrt(somma_quadrati_umid / (n_valori - 1))
    else:
        deviazione_temp = 0
        deviazione_umid = 0

    print(f"Deviazione standard temperatura: {deviazione_temp}")
    print(f"Deviazione standard umidità: {deviazione_umid}")

else:
    print("Nessun dato trovato.")

client.close()