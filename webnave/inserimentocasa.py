# IoT
#
# DB NO-SQL
#
# Inserimento dati sensori nel DBMongo in cloud Atlas con generazione chiave _id automatica
# Cloud Atlas: https://account.mongodb.com/account/login
#
# Dati provenienti dal modulo locale rilevazione_misure_hotel.py
# Formato JSON
#
# Script inserimentocasa.py
#
import time
import json
import random
import pymongo    # MongoDB Driver per Python
from datetime import datetime
#
import rilevazione_misure_case  # Modulo che fornisce una misura in formato JSON
#
#
# Connection string
# mongodb+srv://<db_username>:<db_password>@cluster1.wdel7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1
#
# Sostituire<db_password> con password 
# Sostituire <db_password> con la password per l'utente del database <db_username>.
# Assicurarsi che tutti i parametri delle opzioni siano codificati in URL
# Evitare : / ? # [ ] @ ! $ & ' ( ) * , ; = %
#
"""
+------------------------------------------------------------------------------+
| user                | MongoDB Roles                 | Password               |
| studente            | readWriteAnyDatabase          | studenteiot2024        |
| visualizzatore      | readAnyDatabase               | solovede2024           |
+------------------------------------------------------------------------------+
"""
uri = "mongodb+srv://studente:studenteiot2024@cluster0.fugqs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = pymongo.MongoClient(uri)   # Connessione
#
db = client.Case    # Database 
mycol = db.misure   # Collezione misure
#

"""
Dato IoT:

{
    "invionumero": 1, 
    "camera": 1,
    "piano": 1,
    "temperaturam": 19.12,
    "umiditam": 64.20,
    "dataeora": 1727283213.159446,
    "casa": "GIOT-001",
    "dc": "DC001-01"
}

"""
for n_inserimenti in range(1,3):
    for blocco in range (1,9):
        invionumero = n_inserimenti
        dato_iot_json = rilevazione_misure_case.osservazione()  # Dato in formato JSON
#
        dato_iot_per_mongo = json.loads(dato_iot_json)     # Trasformazione JSON in dizionario per operare con mongo
        dato_iot_per_mongo['invionumero'] = invionumero     
        dato_iot_per_mongo["camera"] = blocco
        dato_iot_per_mongo["dc"] = dato_iot_per_mongo["dc"] + str(blocco)
        #if blocco == 8:
           #dato_iot_per_mongo['temperaturam'] =round(random.uniform(42,44), 2)
            # dato_iot_per_mongo['temperaturam'] = 999
            # dato_iot_per_mongo['umiditam'] = 999
        print("Misure per inserimento")
        print(dato_iot_per_mongo)
        print()
#
        inserimento = mycol.insert_one(dato_iot_per_mongo)  # Inserimento nella collezione
    time.sleep(60)
# 
# il driver MongoDB genera automaticamente un ObjectId per il campo _id
# I valori ObjectId sono lunghi 12 byte e sono composti da:
# Un timestamp di 4 byte, che rappresenta la creazione di ObjectId, misurato in secondi dall'epoca Unix.
# Un valore casuale di 5 byte generato una volta per processo. Questo valore casuale è univoco per la macchina e il processo.
# Un contatore incrementale di 3 byte, inizializzato a un valore casuale.
#
print("Verifica inserimento")
risultato = mycol.find()    # Recupero di tutti i documenti con find() senza condizioni di filtro
if risultato:               # True esistono documenti, False non esistono documenti
    print ()
    for documento in risultato:
        print (documento)    # Dizionario
        print ()
else:
    print("Non esistono documenti")

#
# Nicola Ceccon - laboratorio LTR
# Novembre 2024
# enneci www.enneci.cloud
# Licenza CC BY-NC
