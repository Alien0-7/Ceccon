# IoT
# 
# PUBLISHER
# DATI FORMATO JSON
# Simulazione
# Misura temperatura in una stanza di una casa
# Topic: casamiarosa/cucina/sensore/tu
# Invio dati IoT al broker
#

import time                              # Libreria tempo e data
import paho.mqtt.client as mqtt          # Libreria MQTT di Paho         
import random                            # Libreria che genera numeri pseudo casuali
import json
import datetime
#
# --------------------------------------------------------------------------
# Funzioni
#
# Simulazione sensore temperatura, da 10 a 30 gradi
# cifre decimali pari a N
def on_temp(N):
    TEMP = round(random.uniform(10,30), N)
    return TEMP
def on_umid():
   umid = random.randint(30,60)
   return umid
#
# --------------------------------------------------------------------------
# Parametri
NSERRA = 1
BROKER_HOST = 'broker.emqx.io'                 # Indirizzo IP del broker MQTT (server Terra in LTR)
TOPIC = "casamiarosa/cucina/sensore/tu"        # Topic
PORTA_BROKER = 1883                            # Porta broker MQTT (default)
QOS = 0                         # Qualità del servizio
KEEPALIVE = 60                  # Intervallo massimo tra comunicaziioni con broker
INTERVALLO = 2                  # Intervallo cattura e invio dati in secondi
#
STANZA = "Cucina"               # Stanza con sensore
# --------------------------------------------------------------------------
# Main
#
client = mqtt.Client()                                    # Istanza client
client.connect(BROKER_HOST, PORTA_BROKER, KEEPALIVE)      # Connessione broker MQTT
client.loop_start()                                       # Threaded interface to the network loop
# 
try:
    while True:
        TEMPERATURA = on_temp(1)       # Acquisizione dati
        UMIDITA = on_umid()
        TS = datetime.datetime.now().timestamp()  # Data e ora in formato timestamp
        # Costruzione formato JSON
        # Dizionario
        Dati = {"STANZA": STANZA, "IDSENSORE": "0021","TIPO": "DHT11","PRODUTTORE": "Joy-It",
        "MODELLO": "KY-015", "TEMP": TEMPERATURA,"UMID": UMIDITA,"TIMESTAMP":TS}
        DATI_JSON = json.dumps(Dati,sort_keys=False, indent=2)
        print ("-----------------------------")
        print (DATI_JSON)
        #
        # Invio della temperatura al Broker MQTT con QoS0
        client.publish(TOPIC,DATI_JSON,QOS)
        #      
        # Ritardo lettura
        time.sleep(INTERVALLO)                      # Attesa
#
except KeyboardInterrupt:
        print ("Stop publisher")   
#
client.loop_stop()                                  # Stop the background thread
client.disconnect()                                 # Disconnessione broker MQTT
#
#
# LTR - marzo 2021 - revisione 2024
# enneci
