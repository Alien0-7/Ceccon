# Allegro Elena, Morari Elia
# 5AI
# FLASK NAVE
# Dashboard monitoraggio temperatura e umidità cabine nave
from flask import Flask, render_template
from datetime import datetime
from flask_mqtt import Mqtt
import json
import pymongo
from datetime import datetime, timezone, timedelta


# Creazione applicazione Flask
app = Flask(__name__)

# Configurazione broker MQTT
app.config['MQTT_BROKER_URL'] = 'broker.emqx.io'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_KEEPALIVE'] = 60

# Parametri del database in Mongo
fileMongo = open("mongo.conf") 
dictMongo = json.load(fileMongo)

# Connessione al database MongoDB
client_mongo = pymongo.MongoClient(dictMongo["uri"])
db = client_mongo[dictMongo["database"]]
collezione = db[dictMongo["collezione"]]

mqtt = Mqtt(app)

# Parametri applicazione
refresh = 5
TOPIC = "iotnavi/GIOT-ElenaAllegro/misure/+/+"

# Strutture dati
dati_per_ponte_cabina = {}
medie_per_ponte_cabina = {}

# ROUTE PRINCIPALE DASHBOARD
@app.route('/')
def dashb():
    ora_corrente = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    struttura = {}

    for ponte in sorted(dati_per_ponte_cabina.keys(), key=int):
        struttura[ponte] = sorted(
            dati_per_ponte_cabina[ponte].keys(),
            key=int
        )

    return render_template(
        "home_nave.html",
        ORA=ora_corrente,
        struttura=struttura,
        REFRESH=refresh
    )

# PAGINA TEMPO REALE
@app.route('/temporeale/<PONTE>/<CABINA>')
def tr(PONTE, CABINA):
    ora_corrente = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    if PONTE in dati_per_ponte_cabina and CABINA in dati_per_ponte_cabina[PONTE]:
        Dati_per_template = dati_per_ponte_cabina[PONTE][CABINA].copy()

    else:
        return render_template(
            'nave_p.html',
            PONTE=PONTE,
            CABINA=CABINA,
            REFRESH=refresh
        )
        
    Dati_per_template['REFRESH'] = refresh
    Dati_per_template['ORA'] = ora_corrente
    Dati_per_template['PONTE'] = PONTE
    Dati_per_template['CABINA'] = CABINA

    return render_template('nave_p.html', **Dati_per_template)

# PAGINA MEDIA GIORNALIERA
@app.route('/giornata/<PONTE>/<CABINA>')
def giornata(PONTE, CABINA):
    ora_corrente = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    inizioOggi = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    inizioDomani = inizioOggi + timedelta(days=1)

    # query MongoDB
    risultati = collezione.find({
        "PONTE": PONTE,
        "CABINA": CABINA,
        "TIMESTAMP": {
	    "$gte": inizioOggi.timestamp(),
	    "$lt": inizioDomani.timestamp()
	}  
    })

    somma_temp = 0
    somma_umid = 0
    campioni = 0
    idSensore = "null"
    produttore = "null"
    tipo = "null"
    modello = "null"
    for r in risultati:
        somma_temp += float(r["TEMP"])
        somma_umid += float(r["UMID"])
        campioni += 1
        if campioni == 1:
          idSensore = r["IDSENSORE"] 
          produttore = r["PRODUTTORE"]
          tipo = r["TIPO"]
          modello = r["MODELLO"]
        

    if campioni > 0:
        media_temp = round(somma_temp / campioni, 2)
        media_umid = round(somma_umid / campioni, 2)
    else:
        media_temp = 0
        media_umid = 0

    Dati_per_template = {
        "PONTE": PONTE,
        "CABINA": CABINA,
        "MEDIA_TEMP": media_temp,
        "MEDIA_UMID": media_umid,
        "CAMPIONI": campioni,
        "ORA": ora_corrente,
        "REFRESH": refresh, 
        "IDSENSORE": idSensore,
        "TIPO": tipo,
        "PRODUTTORE": produttore,
        "MODELLO": modello
    }

    return render_template("giornata.html", **Dati_per_template)

# MQTT CONNECT
@mqtt.on_connect()
def gestione_connect(client, userdata, flags, rc):
    print("Connect-Client:", client)
    mqtt.subscribe(TOPIC)

# MQTT SUBSCRIBE
@mqtt.on_subscribe()
def gestione_subscribe(client, userdata, mid, granted_qos):
    print("Subscribe-Client:", client)

# MQTT MESSAGE
@mqtt.on_message()
def gestione_message(client, userdata, message):
    topic = message.topic
    try:
        dati = json.loads(message.payload.decode())
    except:
        print("Errore JSON ricevuto")
        return

    print("JSON ricevuto:", dati)

    parti = topic.split('/')
    ponte = parti[-2]
    cabina = parti[-1]

    # Controllo chiavi
    if "TEMP" not in dati or "UMID" not in dati:
        print("Chiavi TEMP o UMID mancanti")
        return

    # Se manca timestamp lo aggiungo
    if "TIMESTAMP" not in dati:
        dati["TIMESTAMP"] = int(datetime.now().timestamp())

    # Salvo ultimo valore
    if ponte not in dati_per_ponte_cabina:
        dati_per_ponte_cabina[ponte] = {}

    dati_per_ponte_cabina[ponte][cabina] = dati
    temp = float(dati["TEMP"])
    umid = float(dati["UMID"])

    # Calcolo medie
    if ponte not in medie_per_ponte_cabina:
        medie_per_ponte_cabina[ponte] = {}

    if cabina not in medie_per_ponte_cabina[ponte]:
        medie_per_ponte_cabina[ponte][cabina] = {
            "media_temp": temp,
            "media_umid": umid,
            "campioni": 1
        }

    else:
        vecchi = medie_per_ponte_cabina[ponte][cabina]
        n = vecchi["campioni"]

        nuova_media_temp = ((vecchi["media_temp"] * n) + temp) / (n + 1)
        nuova_media_umid = ((vecchi["media_umid"] * n) + umid) / (n + 1)

        medie_per_ponte_cabina[ponte][cabina] = {
            "media_temp": round(nuova_media_temp, 2),
            "media_umid": round(nuova_media_umid, 2),
            "campioni": n + 1
        }

    print("Media aggiornata:", medie_per_ponte_cabina[ponte][cabina])
    
    # === INSERIMENTO IN MONGODB ===
    # Inserimento dei dati nel database
    try:
        dato_per_mongo = dati.copy()
        dato_per_mongo["PONTE"] = ponte
        dato_per_mongo["CABINA"] = cabina
        collezione.insert_one(dato_per_mongo) # Inserimento dentro "misure"
        print("[DEBUG]: dato inserito correttamente in MongoDB")

    except Exception as e:
        print("[ERRORE MongoDB]:", e)

# MQTT DISCONNECT
@mqtt.on_disconnect()
def gestione_disconnect(client, userdata, rc):

    print("Disconnect-Client:", client)

# MQTT LOG
@mqtt.on_log()
def gestione_logging(client, userdata, level, buf):
    print(level, buf)

# AVVIO SERVER FLASK
app.run(host='0.0.0.0', port=5000)
print("Server interrotto manualmente con CTRL+C")
