import socket
import json
import sys

hostname = "127.0.0.1"
portasocket = 9091

maxconnessionicoda = 5                           # numero massimo di connesioni in coda
famiglia = socket.AF_INET                        # socket IPv4
tipo = socket.SOCK_STREAM                        # socket tipo stream TCP
bufferdati = 512                                 # dimensione max buffer dati in ricezione
serversocket = socket.socket(famiglia,tipo)      # creazione socket IP/stream di benvenuto

serversocket.bind((hostname, portasocket))       # lega il socket a IP/porta mediante una tuple
serversocket.listen(maxconnessionicoda)          # attesa connessioni al socket

FORMAT = 'UTF-8'

try:
    while True:
        print("----------------------------------------------")
        print("Server IOTP in ascolto su porta: ", portasocket)
        print("----------------------------------------------\n")

        clientDA_soc,indirizzo = serversocket.accept()
        print("Indirizzo DA: ", indirizzo)
        ricezione = 0
        try:

            while True:
                dati = clientDA_soc.recv(bufferdati).decode(FORMAT)
                
                with open("iotdata.dbt", "a") as f:
                    f.write(json.dumps(dato_iot_dc_json, sort_keys=True))

        except KeyboardInterrupt:
            print("Stop forzata server")
            print("Misurazioni ricevute:",ricezione)
            break


except KeyboardInterrupt:
    print("Stop forzata server")
    clientDA_soc.close()
    serversocket.close()
    sys.exit()