# server che riceve le anomalie di archivia_iotp e salva sul file heartbeat.log
# deve essere UDP
# SERVER UDP
#
import socket
import archivia
socketUDP = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)      # UDP

udp_host = "127.0.0.1"             # Server IP
udp_port = 11111                   # Porta server
socketUDP.bind((udp_host,udp_port))
#
print ("Attesa client...")
try:
    while True:
        dati,indirizzo_client = socketUDP.recvfrom(1024)         # ricezione dati dal client
        print ("Ricezione:",dati.decode()," da",indirizzo_client)
        archivia("heartbeat.log", "a", dati.decode()+"\n")
except KeyboardInterrupt:
    print ("chiusura server")
finally:
    socketUDP.close()