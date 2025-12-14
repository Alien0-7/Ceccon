'''
Allegro Elena, Morari Elia 
5AI

Script archivia_iotp.py (Subscriber)
'''
from datetime import datetime, timezone
import socket
import json
import sys
import cripto 
import paho.mqtt.client as mqtt
import archivia
import threading
import time

# Parametri del file "iotp.json" (topic, dbfile)
file = open("iotp.json") 
dict = json.load(file)

dict_db = dict["dbfile"]

fileP = open("../DA/parametri.json")
dictP = json.load(fileP)

TEMPO_INVIO = dictP["TEMPO_INVIO"]

# Costanti per connessione MQTT
KEEPALIVE = 60
QOS = 0
FORMAT = 'UTF-8'
ricezione = 0  # Variabile che conta i messaggi ricevuti
TT = 1.75  # Coefficiente di tolleranza ai guasti
HEARTBEAT_TIMEOUT = TEMPO_INVIO * 60 * TT

def controllore(socketUDP, udp_host, udp_port):
    global last_message_time
    # WATCHDOG -> funzione o timer che monitora un processo,
    # se il processo non risponde in tempo, il watchdog segnala il problema

    while True:
        if time.time() - last_message_time > HEARTBEAT_TIMEOUT:
            print("Nessun messaggio ricevuto da troppo tempo! Prendo provvedimenti...")
            dati = { 
                "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "level": "WARNING",
                "evento": "HEARTBEAT_TIMEOUT",
                "identita_da": dictP["IDENTITA_DA"],
                "codice": dictP["CODICE"],
                "ultimo_heartbeat": datetime.fromtimestamp(last_message_time, timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "heartbeat_timeout_min": 8,
                "stato": "OFFLINE",
                "azione": "Notifica inviata"
            }
            dati_json = json.dumps(dati) # Conversione in stringa JSON
            dati_b = (dati_json+"\n").encode(FORMAT) # "\n" per segnalare la fine del messaggio
            # Invio il messaggio ad un server UDP
            socketUDP.sendto(dati_b, (udp_host, udp_port))
            last_message_time = time.time()
        time.sleep(1)

# Funzione per la connessione al server IOT
def on_connectIOT(client, userdata, flags, reasone_code, properties):

    if reasone_code == mqtt.CONNACK_ACCEPTED:
        client.subscribe(dict["topic"], QOS)
        print("----------------------------------------------")
        print("Server IOTP in ascolto su MQTT: ",dict["broker"]["host"]+": "+str(dict["broker"]["porta"]))
        print("Iscritto al topic: ",dict["topic"])
        print("----------------------------------------------\n")

    else:
        print("Connessione fallita, codice:",reasone_code)

# Decodifica del payload 
def on_messageIOT(client, userdata, msg):
    dato = msg.payload.decode(FORMAT)
    dato_decriptato = cripto.decriptazione(dato)
    archivia.archivia(dict_db["file"], dict_db["modo"], str(dato_decriptato+"\n"))
    print("[DEBUG]: misura ricevuta, aggiornato il file dbt")
    print("----------------------------------------------\n")
    print("Messaggio ricevuto nel topic:", msg.topic)
    print("Payload:", cripto.decriptazione(msg.payload.decode(FORMAT)))
    print("----------------------------------------------\n")

def on_messageHeartbeat(client, userdata, msg):
    global last_message_time
    last_message_time = time.time()   # Aggiorna il timestamp
    print("[DEBUG]: Heartbeat ricevuto, aggiornato il timestamp")
    print("----------------------------------------------\n")
    print("Messaggio ricevuto nel topic:", msg.topic)
    print("Payload:", msg.payload.decode(FORMAT))
    print("----------------------------------------------\n")

# Main
global last_message_time
last_message_time = time.time()

# Subscriber che riceve i messaggi di heartbeat che invia il DA in un topic apposito
subscriberHeartbeat = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
subscriberHeartbeat.on_message = on_messageHeartbeat
subscriberHeartbeat.connect(dict["broker"]["host"], dict["broker"]["porta"], KEEPALIVE)
subscriberHeartbeat.subscribe("iotnavi/GIOT-EliaMorari/heartbeat", QOS)

# Subscriber che riceve i messaggi che invia il DA nel topic
subscriberIOT = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
subscriberIOT.on_connect = on_connectIOT
subscriberIOT.on_message = on_messageIOT
subscriberIOT.connect(dict["broker"]["host"], dict["broker"]["porta"], KEEPALIVE)

# Costanti socket UDP
socketUDP = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
udp_host = "127.0.0.1"
udp_port = 11111

try:
    threading.Thread(target=controllore, args=(socketUDP, udp_host, udp_port), daemon=True).start()
    subscriberIOT.loop_start()     # Network loop senza blocco infinito
    subscriberHeartbeat.loop_start()     # Network loop senza blocco infinito

    while True:
        pass

except KeyboardInterrupt:
    print("Stop forzato")
    subscriberHeartbeat.loop_stop()
    subscriberIOT.loop_stop()
    sys.exit()