'''
Allegro Elena, Morari Elia 
5AI

Script dc.py --> diventa main.py così che il MCU quando viene collegato parta già da solo
'''
import time
import socket
import sys
import json
import misurazione
import wifidc
import esp         # Libreria per gestire la MCU ESP32
import network

# Parametri della rete Wifi
file_wifi = open("wifipico.conf")  # Parametri del Wifi (nome e password)
dict_wifi = json.load(file_wifi)

wlan = network.WLAN(network.STA_IF)  # Interfaccia modalità stazione per connessione a un AP
wlan.active(True)                    # Attiva interfaccia WiFi
#wlan = network.WLAN(network.AP_IF)  # Interfaccia mdalità AP per altri raspberry Pico W
wifidc.Disabilita_PowerSaving_Mode(wlan)

ssid, psw = wifidc.Parametri_WiFi()

# Connessione alla rete Wifi
wifidc.Connessione_WiFi(wlan, 10, ssid, psw, 1)
print("CONNESSO AL WIFI:\n SSID:",ssid,"\n PSW:",psw)

file_info_socket = open("da.conf") # File con all'interno l'IP e la porta del DA
dict_info_socket = json.load(file_info_socket)

hostname = dict_info_socket["IP"]
portasocket = dict_info_socket["porta"]

# Parametri per la comunicazione TCP
famiglia = socket.AF_INET
tipo = socket.SOCK_STREAM
bufferdati = 64

try:
    clientsocket = socket.socket(famiglia,tipo)
except Exception as errore: # socket.error da l'errore: "AttributeError: 'module' object has no attribute 'error'"
    print(f"Errore creazione socket... \n{errore}")
    sys.exit()

# Tentativo di connessione al DA
while True:
    try:
        print("[DEBUG] Connessione a:",hostname, "porta:",portasocket)
        clientsocket.connect((hostname, portasocket))
        break
    except Exception as errore: # socket.error da l'errore: "AttributeError: 'module' object has no attribute 'error'"
        print(f"Errore creazione connessione... \n{errore}")
        time.sleep(3) 

FORMAT = 'UTF-8'
TEMPO_RILEVAZIONE = 0
N_DECIMALI = 2   # Numero di decimali per le misurazioni

letture = 0   # Contatore delle letture effettuate

file_conf = open("configurazionedc.conf")   # File per la configurazione del DC
dict_conf = json.load(file_conf)

try:
    clientsocket.send("getTempoRilevazione\n".encode())
    tempo_raw = clientsocket.recv(4096).decode(FORMAT) # Attende la risposta del DA
    try:
        TEMPO_RILEVAZIONE = int(tempo_raw)
        print("[DEBUG]", "tempo rilevazione ricevuto dal server:",TEMPO_RILEVAZIONE)
    except Exception:
        print("ERRORE")
        sys.exit()
    

    while True:
        letture += 1

        temperatura, umidita = misurazione.leggi() # Lettura sensore DHT
        
        print("[DEBUG]", "Invio da DC1 temperatura n.",letture,":", temperatura)
        print("[DEBUG]", "Invio da DC1 umidità n.",letture,":", umidita)

        dati = {"cabina": dict_conf["cabina"],"ponte": dict_conf["ponte"],
        "sensore": {"nome": dict_conf["sensore"]["nome"], "tmin": dict_conf["sensore"]["tmin"], "tmax": dict_conf["sensore"]["tmax"], "umin": dict_conf["sensore"]["umin"], "umax": dict_conf["sensore"]["umax"], "erroret": dict_conf["sensore"]["erroret"], "erroreu": dict_conf["sensore"]["erroreu"]},
        "identita_dc": dict_conf["identita_dc"], 
        "osservazione": {"RILEVAZIONE": letture, "TEMP": temperatura, "UMID": umidita}
        }
        
        dati_json = json.dumps(dati) # Conversione in stringa JSON
        dati_b = (dati_json+"\n").encode(FORMAT) # "\n" per segnalare la fine del messaggio
        
        clientsocket.send(dati_b)
        time.sleep(TEMPO_RILEVAZIONE) # Attesa prima della prossima rilevazione

except KeyboardInterrupt:
        clientsocket.send("close".encode(FORMAT)) # Avvisa il DA di chiudere la connessione
        clientsocket.close()
        print ("Stop forzato")

except Exception as error: # socket.error da l'errore: "AttributeError: 'module' object has no attribute 'error'"
    print(f"Errore... \n{error}")
