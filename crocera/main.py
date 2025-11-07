'''
Allegro Elena, Morari Elia 
5AI

Script dc.py
'''
import socket
import time
import sys
import json
import misurazione_dht
import wifidc
import rp2
import network

file_wifi = open("wifipico.json")
dict_wifi = json.load(file_wifi)

rp2.country('IT')                    # Disponibili i canali wifi Italia per evitare possibili errori
wlan = network.WLAN(network.STA_IF)  # Interfaccia modalità stazione per connessione a un AP
wlan.active(True)                    # Attiva interfaccia WiFi
#wlan = network.WLAN(network.AP_IF)  # Interfaccia mdalità AP per altri raspberry Pico W
wifidc.Disabilita_PowerSaving_Mode(wlan)

ssid, psw = wifidc.Parametri_WiFi()

wifidc.Connessione_WiFi(wlan, 10, ssid, psw, 1)

file_info_socket = open("da.json")
dict_info_socket = json.load(file_info_socket)

hostname = dict_info_socket["IP"]
portasocket = dict_info_socket["porta"]
famiglia = socket.AF_INET
tipo = socket.SOCK_STREAM
bufferdati = 64

try:
    clientsocket = socket.socket(famiglia,tipo)
except Exception as errore: # socket.error da l'errore: "AttributeError: 'module' object has no attribute 'error'"
    print(f"Errore creazione socket... \n{errore}")
    sys.exit()

try:
    clientsocket.connect((hostname, portasocket))

except Exception as errore: # socket.error da l'errore: "AttributeError: 'module' object has no attribute 'error'"
    print(f"Errore creazione connessione... \n{errore}")
    sys.exit()

FORMAT = 'UTF-8'
TEMPO_RILEVAZIONE = 0
N_DECIMALI = 2

letture = 0

file_conf = open("configurazionedc.json")
dict_conf = json.load(file_conf)

try:
    clientsocket.send("getTempoRilevazione".encode())
    tempo_raw = clientsocket.recv(4096).decode(FORMAT)
    try:
        TEMPO_RILEVAZIONE = int(tempo_raw)
        print("[DEBUG]", "tempo rilevazione ricevuto dal server:",TEMPO_RILEVAZIONE)
    except Exception:
        print("ERRORE")
        sys.exit()
    

    while True:
        letture += 1
        temperatura, umidita = misurazione_dht.leggi()
        print("[DEBUG]", "Invio da DC1 temperatura n.",letture,":", temperatura)
        print("[DEBUG]", "Invio da DC1 umidità n.",letture,":", umidita)

        dati = {"cabina": dict_conf["cabina"],"ponte": dict_conf["ponte"],
        "sensore": {"nome": dict_conf["sensore"]["nome"], "tmin": dict_conf["sensore"]["tmin"], "tmax": dict_conf["sensore"]["tmax"], "umin": dict_conf["sensore"]["umin"], "umax": dict_conf["sensore"]["umax"], "erroret": dict_conf["sensore"]["erroret"], "erroreu": dict_conf["sensore"]["erroreu"]},
        "identita_dc": dict_conf["identita_dc"], 
        "osservazione": {"RILEVAZIONE": letture, "TEMP": temperatura, "UMID": umidita}
        }
        
        dati_json = json.dumps(dati)
        dati_b = dati_json.encode(FORMAT)
        
        clientsocket.send(dati_b)
        time.sleep(TEMPO_RILEVAZIONE)

except KeyboardInterrupt:
        clientsocket.send("close".encode(FORMAT))
        clientsocket.close()
        print ("Stop forzato")

except Exception as error: # socket.error da l'errore: "AttributeError: 'module' object has no attribute 'error'"
    print(f"Errore... \n{error}")