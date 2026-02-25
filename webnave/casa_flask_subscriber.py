# IoT
# MQTT e PYTHON
# SUBSCRIBER
# DATI FORMATO JSON
#
# Simulazione
# Misura temperatura in una serra
# Topic: casamiarosa/cucina/sensore/tu
# Ricezione dati IoT dal broker formato JSON
#
# Test:
# avviare casa_dc_publisher.py
# utilizzare come URL 127.0.0.1:5000 o IP:5000
# utilizzare curl -v http://127.0.0.1:5000
# utilizzare curl http://127.0.0.1:5000  -o risposta.json per acquisire la pagina
#
from flask import Flask, render_template
from datetime import timedelta, datetime
from time import time
from flask_mqtt import Mqtt
"""
   Viene utilizzata la libreria specifica per flask
   Sì, può usare Paho-MQTT in Flask invece di Flask-MQTT
   Tuttavia, Flask-MQTT è un'estensione specifica per Flask che semplifica l'integrazione con MQTT,
   mentre Paho-MQTT è una libreria generica per MQTT.
   Questo comporta che per usare Paho-MQTT direttamente in Flask, si deve gestire il client MQTT
   in un thread separato per evitare di bloccare l'esecuzione del server Flask.
   
   import paho.mqtt.client as mqtt
   import threading
   ...
   mqtt_thread = threading.Thread(target=mqtt_loop, daemon=True)
   mqtt_thread.start()
   
   Quindi, i vantaggi di Flask-MQTT sono:
       1) Gestione del loop MQTT senza bisogno di un thread separato
       2) Integrazione con Flask in modo più nativo
       3) Funzioni già pronte per la gestione di eventi MQTT
"""   
import json
"""
   Si utilizza la libreria standard di serializzazione e deserilizzaione di Python,
   Flask dispone di una libreria specifica, ottimizzata di nome jsonify.
   
   import jsonify
"""
#
app = Flask(__name__)
# Configurazione MQQT Server (Broker)
app.config['MQTT_BROKER_URL'] = 'broker.emqx.io' 
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_KEEPALIVE'] = 60
#
mqtt = Mqtt(app)
# Parametri
refresh = 5                                 # Tempo in secondi per il refresh della dashboard
TOPIC = "casamiarosa/cucina/sensore/tu"     # Topic
# 
# Route
#  
@app.route('/') # root route (default page)
def dashb():
    Dati_per_template = json.loads(dati_json_da_publisher)              # Conversione da JSON
    Dati_per_template['REFRESH'] =  refresh                             # Agggiunta refresh
    data_ora = datetime.fromtimestamp(Dati_per_template['TIMESTAMP'])
    formato = "%d-%m-%Y %H:%M"
    Dati_per_template['ORARIO'] = datetime.strftime(data_ora,formato)   # Data e ora umana
    print (Dati_per_template)                                           # Debug
    return render_template("casa_mqtt_json.html",**Dati_per_template)   # Passaggio dizionario con scompattamento
    """
    Il doppio asterisco (**) scompatta un dizionario e passa ogni chiave come variabile al template
    indica, quindi, il passaggio di un dizionario di parametri
    e nel template si accede al parametro direttamente con il nome
    L'asterisco singolo indica una tupla, ma si usa poco.
    Una tupla in Python è una struttura dati immutabile, simile a una lista,
    ma che non può essere modificata dopo la creazione.
    Si definisce usando parentesi tonde () e può contenere elementi di qualsiasi tipo
    e gli elementi hanno un indice come li liste, quindi si accede con nome_tupla(0)
    al primo elemento. Si usa quando ho dati immodificabili per velocizzare l'accesso
    agli elemnti rispetto ad una lista. Una tupla si converte il lista con .list,
    nome_lista = list(nome_tupla) per modificarla e poi si ritrasforma in tupla con .tuple,
    nome_tupla = tuple(nome_lista)
    """
#
# MQTT client subscriber
#
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
    global dati_json_da_publisher                                   # FONDAMENTALE
    topic = message.topic
    dati_json_da_publisher = message.payload.decode()
    print ("topic: ",topic,"\n - dati: \n",dati_json_da_publisher)  # Debug
    return dati_json_da_publisher
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
