'''
Allegro Elena, Morari Elia 
5AI

Script iotgwda.py (publisher)
'''
import socket
import threading
import json
import sys
import time
import cripto
import paho.mqtt.client as mqtt

# Creazione server DA 
f = open("parametri.json")  
dict = json.load(f)

f_da = open("../da.json")
dict_da = json.load(f_da)

hostname = dict_da["IP"]
portasocket = dict_da["porta"]

dati_ricevuti = {}

# SOCKET --> connessione con il DC 
maxconnessionicoda = 5                           # numero massimo di connesioni in coda
famiglia = socket.AF_INET                        # socket IPv4
tipo = socket.SOCK_STREAM                        # socket tipo stream TCP
bufferdati = 512                                 # dimensione max buffer dati in ricezione
serversocket = socket.socket(famiglia,tipo)      # creazione socket IP/stream di benvenuto

serversocket.bind((hostname, portasocket))       # lega il socket a IP/porta mediante una tuple
serversocket.listen(maxconnessionicoda)          # attesa connessioni al socket

# MQTT --> connessione con Archivia_iotp 
KEEPALIVE = 60
QOS = 0

client = mqtt.Client(callback_api_version = mqtt.CallbackAPIVersion.VERSION2) # MQTTv311 (VERSION2)
client.connect(dict["BROKER"], dict["PORTA_BROKER"], KEEPALIVE)       # Connessione broker MQTT
client.loop_start()                                        # Threaded interface to the network loop (asincronia)

# Costanti
FORMAT = 'UTF-8'
TEMPO_RILEVAZIONE = dict["TEMPO_RILEVAZIONE"]
N_DECIMALI = 2    # Numero di decimali nelle medie
stop_thread = threading.Event()

# Funzione che calcola periodicamente la media di temperatura e umidità
def calcola_media(tempo_invio):
    invionumero = 1

    while not stop_thread.is_set():
        time.sleep(tempo_invio * 60) # Attesa tra un invio e l'altro

        dati_ricevuti_copia = json.loads(json.dumps(dati_ricevuti)) # per evitare RuntimeError: dictionary changed size during iteration

        # Il set contiene SOLO valori diversi (unici) tra loro
        identita_dc_unici = set(d["identita_dc"] for d in dati_ricevuti_copia.values())

        for identita_dc in identita_dc_unici:
            temp_media = 0
            umid_media = 0
            ricezioni = 0
            cabina = 0
            ponte = 0

            for d in dati_ricevuti_copia.values():
                if d["identita_dc"] == identita_dc:
                    temp_media += d["osservazione"]["TEMP"]
                    umid_media += d["osservazione"]["UMID"]
                    ricezioni += 1
                    cabina = d["cabina"]
                    ponte = d["ponte"]

            if ricezioni == 0:
                continue

            dato_iot_dc_json = {
                "nave": "CrocieraCeccon",
                "invionumero": invionumero,
                "cabina": cabina,
                "ponte": ponte,
                "temperaturam": round(temp_media / ricezioni, dict["N_DECIMALI"]),
                "umiditam": round(umid_media / ricezioni, dict["N_DECIMALI"]),
                "dataeora": time.time() * 1000,
                "identita_da": dict["IDENTITA_DA"],
                "identita_dc": identita_dc
            }

            print("[DEBUG]: Dato DC da criptare:\n" ,dato_iot_dc_json,"\n")

            # Criptazione del dato tramite la funzione "criptazione" del file "cripto.py"
            dato_iot_dc_json_criptato = cripto.criptazione(json.dumps(dato_iot_dc_json, indent=4, sort_keys=True))

            print("[DEBUG]: Dato DC criptato:\n" ,dato_iot_dc_json_criptato,"/n")
            
            # Invio dei dati all'archivio IOTP
            try:
                RETAIN = False
                client.publish(dict["TOPIC"], dato_iot_dc_json_criptato.encode(FORMAT), QOS, RETAIN)
                invionumero += 1
                    
            except Exception:
                print("ERRORE durante l'invio dei dati criptati")
                stop_thread.set()
                return


try:
    t = threading.Thread(target=calcola_media, args=(dict["TEMPO_INVIO"],))
    t.daemon = True
    t.start()

    while True:
        print("----------------------------------------------")
        print("Server in ascolto su porta: ", portasocket)
        print("----------------------------------------------\n")

        # Attesa di connessione da un DC 
        client_soc,indirizzo = serversocket.accept()
        print("Indirizzo DC: ", indirizzo)
        ricezione = 0
        dati = ""

        try:

            while True:
                dati_part = client_soc.recv(bufferdati).decode(FORMAT)
                dati += dati_part

                # Se il client chiude la connessione
                if not dati_part:
                    print("Connessione chiusa dal client")
                    stop_thread.set()
                    t.join()
                    break

                # Se non è ancora arrivato "\n", continua
                if "\n" not in dati:
                    continue
                
                linea, dati = dati.split("\n", 1)
                # print("[DEBUG] Linea ricevuta:\n", linea)
                if linea == "getTempoRilevazione":
                    string = str(TEMPO_RILEVAZIONE).encode(FORMAT)
                    client_soc.send(string)
                
                elif linea == "close":
                    stop_thread.set()
                    t.join()
                    break
                    
                
                else:
                    # Ricezione dati dal sensore
                    try:
                        ricezione += 1
                        print("[DEBUG]", "Ricezione dati n.",ricezione,":\n", json.dumps(json.loads(linea), indent=4, sort_keys=True))
                        dati_ricevuti[ricezione] = json.loads(linea)
                    except Exception as error:
                        print("Errore decodifica dati ricevuti:\n", linea)
                        stop_thread.set()
                        t.join()
        except KeyboardInterrupt:
            print("Stop forzata server")
            print("Misurazioni ricevute:",ricezione)
            break


except KeyboardInterrupt:
    print("Stop forzata server")
    client_soc.close()
    serversocket.close()
    client.loop_stop()
    sys.exit()


