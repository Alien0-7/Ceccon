'''
Allegro Elena, Morari Elia 
5AI

Script analisi_iotp.py
'''
import json
import pymongo
import math

file = open("mongo.conf") 
dict = json.load(file)
uri = dict['uri']
db_name = dict['database']
collezione = dict['collezione']

client = pymongo.MongoClient(uri)

db = client["Nave2025"]
collezione = db["misure"]

print("Inserisci i parametri di ricerca:")
nave = input("Nome nave: ")
giorno = int(input("Giorno (GG): "))
mese = int(input("Mese (MM): "))
anno = int(input("Anno (AAAA): "))
cabina = input("Cabina: ")

query = {
    "nave.nome": nave,
    "cabina": cabina,
    "dataeora": {
        "$gte": f"{anno:04d}-{mese:02d}-{giorno:02d}T00:00:00Z",
        "$lte": f"{anno:04d}-{mese:02d}-{giorno:02d}T23:59:59Z"
    }
}

esito = collezione.find(query)

if (esito):
    print("[DEBUG] Documenti trovati:")
    lista_documenti = list(esito) # Converti il cursore in una lista per poterlo iterare più volte
    
    n_valori = len(lista_documenti)
    print(f"Numero di misurazioni trovate: {n_valori}")

    media_temp = 0.0
    media_umid = 0.0
    for documento in lista_documenti:
        media_temp += documento["temperaturam"]
        media_umid += documento["umiditam"]
    
    media_temp /= n_valori
    media_umid /= n_valori

    print(f"Media temperatura: {media_temp} °C")
    print(f"Media umidità: {media_umid} %")

    somma_quadrati_temp = 0.0
    somma_quadrati_umid = 0.0

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