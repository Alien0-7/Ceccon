'''
Allegro Elena, Morari Elia 
5AI

Script archivia_iotp.py
'''
import socket
import json
import sys
import cripto 
import paho.mqtt.client as mqtt
import archivia
import threading
import time

file = open("iotp.json")  # Parametri del Wifi (nome e password)
dict = json.load(file)

dict_db = dict["dbfile"]

KEEPALIVE = 60
QOS = 0
FORMAT = 'UTF-8'
ricezione = 0       # Variabile che conta i messaggi ricevuti
TT = 1.75  # coefficiente di tolleranza ai guasti
TEMPO_RILEVAZIONE = 2
HEARTBEAT_TIMEOUT = TEMPO_RILEVAZIONE*60*TT

def controllore(socketUDP, udp_host, udp_port):
    # WATCHDOG -> funzione o timer che monitora un processo,
    # se il processo non risponde in tempo, il watchdog segnala il problema

    while True:
        if time.time() - last_message_time > HEARTBEAT_TIMEOUT:
            print("Nessun messaggio ricevuto da troppo tempo! Eseguo azione...")
            dati = { 
                "timestamp": "2025-11-23T14:32:41Z",
                "level": "WARNING",
                "evento": "HEARTBEAT_TIMEOUT",
                "identita_da": "GIOT-1",
                "codice": "108EX",
                "ultimo_heartbeat": "2025-11-23T14:25:12Z",
                "heartbeat_timeout_min": 8,
                "stato": "OFFLINE",
                "azione": "Notifica inviata"
            }
            dati_json = json.dumps(dati) # Conversione in stringa JSON
            dati_b = (dati_json+"\n").encode(FORMAT) # "\n" per segnalare la fine del messaggio
            socketUDP.sendto(dati_b, (udp_host, udp_port))
            last_message_time = time.time()
        time.sleep(1)


def on_connectIOT(client, userdata, flags, reasone_code, properties):
    if reasone_code == mqtt.CONNACK_ACCEPTED:
        print("----------------------------------------------")
        print("Server IOTP in ascolto su mqtt:",dict["broker"]["host"]+":"+dict["broker"]["port"])
        print("----------------------------------------------\n")
        client.subscribe(dict["topic"], QOS)
    else:
        print("Connessione fallita, codice:",reasone_code)

def on_messageIOT(client, userdata, msg):
    dato = msg.payload.decode(FORMAT)
    archivia(dict_db["file"], dict_db["modo"], dato)
    

def on_connectHeartbeat(client, userdata, flags, reasone_code, properties):
    global last_message_time

def on_messageHeartbeat(client, userdata, msg):
    last_message_time = time.time()   # aggiorna il timestamp


subscriberIOT = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
subscriberIOT.on_connect = on_connectIOT
subscriberIOT.on_message = on_messageIOT
subscriberIOT.connect(dict["broker"]["host"], dict["broker"]["port"], KEEPALIVE)

subscriberHeartbeat = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
subscriberHeartbeat.on_connect = on_connectHeartbeat
subscriberHeartbeat.on_message = on_messageHeartbeat
subscriberHeartbeat.connect("iotnavi/+/heartbeat", dict["broker"]["port"], KEEPALIVE)

socketUDP = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
udp_host = "127.0.0.1"
udp_port = 11111

try:
    threading.Thread(target=watchdog, daemon=True).start()
    subscriberIOT.loop_start()     # Network loop senza blocco infinito
    subscriberHeartbeat.loop_start()     # Network loop senza blocco infinito
    while True:
        pass
except KeyboardInterrupt:
    print("Stop forzato")
    subscriberHeartbeat.loop_stop()
    subscriberIOT.loop_stop()
    sys.exit()
