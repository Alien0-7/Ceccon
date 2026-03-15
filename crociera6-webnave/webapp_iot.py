# 
# FLASK NAVE
# Host default IP dell'host (con 127.0.0.1 connessione negata)
# Porta default 5000
#
# Script nave.py
#
from flask import Flask, render_template
from datetime import timedelta, datetime
from time import time
from flask_mqtt import Mqtt
import json
#
app = Flask(__name__)            # Istanza della classe

app.config['MQTT_BROKER_URL'] = 'broker.emqx.io' 
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_KEEPALIVE'] = 60
#
mqtt = Mqtt(app)
# Parametri
refresh = 5                             # Tempo in secondi per il refresh della dashboard
TOPIC = "iotnavi/GIOT-EliaMorari/misure/+/+"     # Topic
dati_per_ponte_cabina = {}              # <-- Aggiunto qui
# Route - URL intercettati
#
@app.route('/')   # Decorator to bind a function to a URL /, route di default http://ip_host:5000
def dashb():
    return("ciao")
    
@app.route('/temporeale/<PONTE>/<CABINA>')
def tr(PONTE, CABINA):
    global dati_per_ponte_cabina

    # Controllo se esistono dati per quella combinazione
    if PONTE in dati_per_ponte_cabina and CABINA in dati_per_ponte_cabina[PONTE]:
        Dati_per_template = dati_per_ponte_cabina[PONTE][CABINA].copy()  # Copia per sicurezza
    else:
        return f"Nessun dato disponibile per PONTE {PONTE} CABINA {CABINA}"

    Dati_per_template['REFRESH'] = refresh

    # Formattazione timestamp in data/ora leggibile
    data_ora = datetime.fromtimestamp(Dati_per_template['TIMESTAMP'])
    formato = "%d-%m-%Y %H:%M:%S"
    Dati_per_template['ORARIO'] = data_ora.strftime(formato)

    return render_template('nave_p.html', **Dati_per_template)

@mqtt.on_connect()
def gestione_connect(client, userdata, flags, rc):
    print("Connect-Client:", client)                                # Debug
    mqtt.subscribe(TOPIC)
#
@mqtt.on_subscribe()
def gestione_subscribe(client, userdata, mid, granted_qos):
    print("Subscribe-Client:", client)                              # Debug
#
@mqtt.on_message()
def gestione_message(client, userdata, message):
    global dati_per_ponte_cabina
    topic = message.topic                  # es: iotnavi/GIOT-EliaMorari/misure/1/3
    payload = message.payload.decode()     # JSON string
    dati = json.loads(payload)             # Conversione in dict
    
    # Estrazione PONTE e CABINA dal topic
    parti = topic.split('/')               # ['iotnavi','GIOT-EliaMorari','misure','1','3']
    ponte = parti[-2]
    cabina = parti[-1]
    
    # Salvataggio nel dizionario globale
    if ponte not in dati_per_ponte_cabina:
        dati_per_ponte_cabina[ponte] = {}
    dati_per_ponte_cabina[ponte][cabina] = dati

    print(f"Ricevuto PONTE {ponte} CABINA {cabina}:\n{dati}")
#
@mqtt.on_disconnect()
def gestione_disconnect(client, userdata, rc):
    print("Disconnect-Client:", client)                             # Debug
#
@mqtt.on_log()
def gestione_logging(client, userdata, level, buf):
    print(level, buf)                                               # Debug
#
# Avvio del server web integrato per eseguire l'applicazione
# rende l'APP accessibile all'indirizzo specificato o di default
# e blocca l'esecuzione dello script finché il server non viene chiuso
#
app.run(host='0.0.0.0',port=5000)
#
print ("Server interrotto manualmente con CTRL+C")
#
# LTR - marzo 2021 - revisione 2024
# enneci
