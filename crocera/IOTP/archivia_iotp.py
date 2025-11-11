'''
Allegro Elena, Morari Elia 
5AI

Script archivia_iotp.py
'''
import socket
import json
import sys
from DA import cripto

hostname = "127.0.0.1"              # Indirizzo IP del server Archivio
portaserver = 9091                  # Porta server Archivio

maxconnessionicoda = 5                           # numero massimo di connesioni in coda
famiglia = socket.AF_INET                        # socket IPv4
tipo = socket.SOCK_STREAM                        # socket tipo stream TCP
bufferdati = 512                                 # dimensione max buffer dati in ricezione
serversocket = socket.socket(famiglia,tipo)      # creazione socket IP/stream di benvenuto

serversocket.bind((hostname, portaserver))       # lega il socket a IP/porta mediante una tuple
serversocket.listen(maxconnessionicoda)          # attesa connessioni al socket

FORMAT = 'UTF-8'

ricezione = 0                       # Variabile che serve per sapere quante volte riceve i dati 

try:
    while True:
        print("----------------------------------------------")
        print("Server IOTP in ascolto su porta: ", portaserver)
        print("----------------------------------------------\n")

        clientDA_soc,indirizzoDA = serversocket.accept()
        print("Indirizzo DA: ", indirizzoDA)
        
        try:

            while True:
                # Dato del DA criptato
                dato_iot_dc_json_criptato = clientDA_soc.recv(bufferdati).decode(FORMAT)   
                
                # Dato del DA decriptato
                dato_iot_dc_json = cripto.decriptazione(json.dumps(dato_iot_dc_json_criptato, sort_keys=True))

                with open("iotdata.dbt", "a") as f:
                    f.write(json.dumps(dato_iot_dc_json, sort_keys=True))
                
                ricezione += 1  

        except KeyboardInterrupt:
            print("Stop forzata server Archivio")
            print("Misurazioni ricevute:",ricezione)
            break


except KeyboardInterrupt:
    print("Stop forzata server")
    clientDA_soc.close()
    serversocket.close()
    sys.exit()