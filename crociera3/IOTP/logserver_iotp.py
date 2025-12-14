'''
Allegro Elena, Morari Elia 
5AI

Script logserver_iotp.py
Server UDP che riceve le anomalie di archivia_iotp e salva sul file heartbeat.log
'''

import socket
import archivia

# Creazione server UDP
socketUDP = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)      # UDP
udp_host = "127.0.0.1"             # Server IP
udp_port = 11111                   # Porta server
socketUDP.bind((udp_host,udp_port))

print ("Attesa client...")
try:
    while True:
        try:
            dati,indirizzo_client = socketUDP.recvfrom(1024)         # ricezione dati dal client
            print ("Ricezione:",dati.decode()," da: ",indirizzo_client)
            # Utilizzo la funzione archivia per salvare il messaggio nel file "heartbeat.log"
            archivia.archivia("heartbeat.log", "a", dati.decode()+"\n")
        
        except KeyboardInterrupt:
            print ("Chiusura server")

        finally:
            socketUDP.close()
        
except KeyboardInterrupt:
    print ("Chiusura server")

finally:
    socketUDP.close()