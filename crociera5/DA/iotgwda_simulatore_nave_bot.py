# IoT
# MQTT e PYTHON
# Simulatore gateway/DA di una nave
# Invio di N_MISURE di N_CABINE con intervallo pari a INTERVALLO in secondi
# con misure anomale per la cabina numero 1
# 
# Script iotgwda_simulatore_nave.py
#
import time                        # Libreria tempo e data
import paho.mqtt.client as mqtt    # Libreria MQTT di Paho         
import random                      # Libreria che genera numeri pseudo casuali
import json
import datetime
import cripto                      # Libreria crittografia
#
# Simulazione sensore temperatura e umidità
# cifre decimali pari a N
def on_temp(N):
   TEMP = round(random.uniform(22,24), N)
   return TEMP
def on_um(N):
   UM = round(random.uniform(40,60), N)
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
f = open("parametri.conf")  
dict = json.load(f)

fman = open("../IOTP/manutenzione.conf")  
dictman = json.load(fman)

BROKER_HOST = 'broker.hivemq.com'             # Server pubblico MQTT hivemq (porta 1883)
PORTA_BROKER = 1883                           # Porta broker MQTT (default)
#
TOPIC = 'iotnavi/GIOT-EliaMorari/misure'                # Topic
#
QOS = 0                                        # Qualità del servizio minima: nessuna garanzia consegna
KEEPALIVE = 60                                 # Tempo massimo che può trascorrere senza comunicazione tra il client e il broker.
INTERVALLO = 20                                # Intervallo cattura e invio dati in secondi
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
time.sleep(5)
#
misura = 0
N_MISURE = 5
N_CABINE = 5
SOGLIA_MISURE = 2
ALLARME = 30   # Da file configurazione
CRITICO = 35
try:
    while misura < N_MISURE:
        misura = misura + 1
        print ("Invio blocco ", misura," delle misure di", N_CABINE, "cabine")
        for cabina in range(1, N_CABINE + 1):
            if cabina == 1 and misura == SOGLIA_MISURE:
                TEMPERATURA = ALLARME + 1
                colore = "\033[33m"         # Testo in giallo
            elif cabina == 1 and misura > SOGLIA_MISURE:
                TEMPERATURA = CRITICO + 1
                colore = "\033[31m"         # Testo in rosso
            else: 
                TEMPERATURA = on_temp(2)    
                colore = "\033[30m"         # Testo in nero
            #
            UMIDITA = on_um(0)
            TS = datetime.datetime.now().timestamp()  # Data e ora in formato timestamp
            # Costruzione formato JSON
            #
            cabina_n = cabina
            ponte_n = 1
            identita_dc = "DC" + str(cabina_n) + "-" + str(ponte_n)
            #
            DATI_JSON = f"""{{
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
            print(colore, DATI_JSON)
            #
            # Invio della temperatura al Broker MQTT con QoS0
            client.publish(TOPIC,DATI_JSON,QOS)
            #    
            if (TEMPERATURA > ALLARME):
                print("ALERT: Temperatura anomala nella cabina", cabina_n, " del ponte ", ponte_n)
                DATI_ALERT = f"""{{
                "ponte": {ponte_n},
                "cabina": {cabina_n},
                "alert": {{
                "soglia": "allarme",
                "temperaturam": {TEMPERATURA},
                "timestamp": {TS},
                "rilevazione": {misura}
                }},
                "identita_dc": "{identita_dc}",
                "pin_segnale": 0,
                "documentazione": {{
                "dms_id": "MAN-{identita_dc}",
                "tipo": "manuale tecnico"
                }}
                }}"""
                client.publish(dictman["topic"]["alert"],cripto.criptazione(DATI_ALERT),QOS)


        # Ritardo lettura
        print("_________________________________________________________________")
        time.sleep(INTERVALLO)                      # Attesa
        print()
#
except KeyboardInterrupt:
        print("Stop publisher")   
#
client.loop_stop()                                  # Stop the background thread
client.disconnect()                                 # Disconnessione broker MQTT
#
# Nicola Ceccon - laboratorio LTR
# Gennaio 2025 - upg dicembre 2026
#
