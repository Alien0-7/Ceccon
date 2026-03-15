# Allegro Elena, Morari Elia 
# 5AI
# PUBLISHER - Simulazione
# Invio dati IoT al broker

import time                              # Libreria tempo e data
import paho.mqtt.client as mqtt          # Libreria MQTT di Paho         
import random                            # Libreria che genera numeri pseudo casuali
import json
import datetime

# Simulazione sensore temperatura, da 10 a 30 gradi
def on_temp(N):
    TEMP = round(random.uniform(10,40), N)
    return TEMP
def on_umid():
   umid = random.randint(30,60)
   return umid

# Parametri
BROKER_HOST = 'broker.emqx.io'                 # Indirizzo IP del broker MQTT (server Terra in LTR)
TOPIC = "iotnavi/GIOT-EliaMorari/misure"        # Topic
PORTA_BROKER = 1883                            # Porta broker MQTT (default)
QOS = 0                         # Qualità del servizio
KEEPALIVE = 60                  # Intervallo massimo tra comunicaziioni con broker
INTERVALLO = 2                  # Intervallo cattura e invio dati in secondi
#
N_CABINE = 5                    # Stanza con sensore
N_PONTI = 3

client = mqtt.Client()                                    # Istanza client
client.connect(BROKER_HOST, PORTA_BROKER, KEEPALIVE)      # Connessione broker MQTT
client.loop_start()                                       # Threaded interface to the network loop

try:
	while True:
		for i in range(N_PONTI):
			PONTE = i+1
			for j in range(N_CABINE):
				CABINA = j+1
				TEMPERATURA = on_temp(2)       # Acquisizione dati
				UMIDITA = on_umid()
				TS = datetime.datetime.now().timestamp()  # Data e ora in formato timestamp
				# Dizionario
				Dati = {"CABINA": CABINA, "PONTE": PONTE, "IDSENSORE": "0021","TIPO": "DHT11","PRODUTTORE": "Joy-It",
				"MODELLO": "KY-015", "TEMP": TEMPERATURA,"UMID": UMIDITA,"TIMESTAMP":TS}
				DATI_JSON = json.dumps(Dati,sort_keys=False, indent=2)
				print ("-----------------------------")
				print (DATI_JSON)
			
				# Invio della temperatura al Broker MQTT con QoS0
				client.publish(str(TOPIC+"/"+str(PONTE)+"/"+str(CABINA)),DATI_JSON,QOS)
				 
				# Ritardo lettura
				time.sleep(INTERVALLO) 
				
except KeyboardInterrupt:
        print ("Stop publisher")   

client.loop_stop()                               
client.disconnect()                               
