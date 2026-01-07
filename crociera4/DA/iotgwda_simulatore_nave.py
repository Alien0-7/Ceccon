# IoT
# MQTT e PYTHON
# Simulatore gateway/DA di una nave
# Invio di N_MISURE di N_CABINE con intervallo pari a INTERVALLO in secondi
# 
# Script iotgwda_simulatore_nave.py
#

import time                        # Libreria tempo e data
import paho.mqtt.client as mqtt    # Libreria MQTT di Paho         
import random                      # Libreria che genera numeri pseudo casuali
import json
import datetime
#
# Simulazione sensore temperatura e umidità
# cifre decimali pari a N


f = open("parametri.conf")  
dict = json.load(f)

def on_temp(N):
   TEMP = round(random.uniform(10,30), N)
   return TEMP
def on_um(N):
   UM = round(random.uniform(50,80), N)
   return UM
#

def on_connect(client, userdata, flags, rc):
# Nel caso della versione paho-mqtt 2.0.0 si deve utilizzare    
# def on_connect(client, userdata, flags, reason_code, properties):
    if rc == 0:
        print ("debug")
        print("Topic subscriber:",TOPIC,"- con QOS:", QOS)
        print("Connesso a MQTT Broker", BROKER_HOST,":",PORTA_BROKER)
        print()
    else:
        print("Connessione fallita, return code %d\n", rc)
#
BROKER_HOST = dict["BROKER"]             # Server pubblico MQTT hivemq (porta 1883)
PORTA_BROKER = dict["PORTA_BROKER"]                           # Porta broker MQTT (default)
#
TOPIC = dict["TOPIC"]                # Topic
#
QOS = 0                                        # Qualità del servizio minima: nessuna garanzia consegna
KEEPALIVE = 60                                 # Tempo massimo che può trascorrere senza comunicazione tra il client e il broker.
INTERVALLO = 2                                 # Intervallo cattura e invio dati in secondi
#
# Main
#
client = mqtt.Client()
# Nel caso della versione paho-mqtt 2.0.0 si deve utilizzare
# client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
#
client.connect(BROKER_HOST, PORTA_BROKER, KEEPALIVE)        # Connessione broker MQTT
client.on_connect = on_connect  # Funzione definita on_connect associata al client in risposta alla connessione avvenuta

client.loop_start()                                         # Threaded interface to the network loop
time.sleep(2)
#
misura = 0
N_MISURE = 10
N_CABINE = 5
try:
    while misura < N_MISURE:
        misura = misura + 1
        print ("Invio blocco misure numero", misura,"di cabine numero",N_CABINE)
        for cabine in range(1, N_CABINE + 1):
            TEMPERATURA = on_temp(2)                  # Acquisizione dati
            UMIDITA = on_um(0)
            TS = datetime.datetime.now().timestamp()  # Data e ora in formato timestamp
            # Costruzione formato JSON
            #
            cabina_n = cabine
            ponte_n = 1
            identita_dc = "DC" + str(cabina_n) + "-" + str(ponte_n)
            #
            dati = f"""{{
            "nave": {{
            "nome": "Rocinante",
            "cabine": 15,
            "passeggeri": 30,
            "equipaggio": 6,
            "ponti": 3,
            "spazi": 2,
            "codice_nave": "108EX"
            }},
            "cabina": {cabina_n},
            "ponte": {ponte_n},
            "temperaturam": {TEMPERATURA},
            "umiditam": {UMIDITA},
            "dataeora": {TS},
            "identita_da": "GIOT-1",
            "identita_dc": "{identita_dc}",
            "invionumero": {misura}
            
            }}"""
            #
            DATI_JSON = dati
            print (DATI_JSON)
            #
            # Invio della temperatura al Broker MQTT con QoS0
            client.publish(TOPIC,DATI_JSON,QOS)
            #      
            # Ritardo lettura
            time.sleep(INTERVALLO)                      # Attesa
        print ()
#
except KeyboardInterrupt:
        print ("Stop publisher")   
#
client.loop_stop()                                  # Stop the background thread
client.disconnect()                                 # Disconnessione broker MQTT
#
# Nicola Ceccon - laboratorio LTR
# Aprile 2021 - upg dicembre 2025
#
