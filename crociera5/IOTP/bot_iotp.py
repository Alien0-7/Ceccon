"""
NEGRO Elena, Morari Elia 
5AI

(subscriber mqtt + bot telegram)
"""

import telepot                                          # Libreria BOT Telegram
from telepot.loop import MessageLoop
import time                                             # Libreria tempo e data
import paho.mqtt.client as mqtt                         # Libreria MQTT di Paho
import json                                             # Libreria JSON
import cripto                                           # Libreria crittografia
from datetime import datetime

def azione(msg):                               # Funzione che viene eseguita ogniqualvolta il bot riceve un messaggio
    global waiting_confirmation
    chat_id = msg['chat']['id']                # Chat 
    comando = msg['text']                      # Comando       

    if comando == '/start':                   # Comando di avvio
        telegram_bot.sendMessage(chat_id, "Bot IOTP attivo e in ascolto per alert di manutenzione.")
    
    elif comando == '/help':                 # Comando di aiuto
        telegram_bot.sendMessage(chat_id,
            "Comandi disponibili:\n"
            "/start - Avvia il bot\n"
            "/help - Mostra i comandi disponibili\n"
            "/subme - Iscriviti agli alert di manutenzione\n"
            "/unsubme - Disiscriviti dagli alert di manutenzione"
)
    
    elif comando == '/subme' and str(chat_id) not in dicttbot["chatids"]:               # Comando per iscriversi agli alert
        telegram_bot.sendMessage(chat_id, "è stata mandata una richiesta di iscrizione agli allert agli amministratori.")
        if len(dicttbot["chatids"]) > 0:
            telegram_bot.sendMessage(1051473816, "Richiesta di iscrizione agli alert di manutenzione da parte di: "+msg['from'].get('first_name','Utente')+"\n confermare con il comando /confirm " + str(chat_id))
            telegram_bot.sendMessage(6199997165, "Richiesta di iscrizione agli alert di manutenzione da parte di: "+msg['from'].get('first_name','Utente')+"\n confermare con il comando /confirm " + str(chat_id))
        else:
            for cid in dicttbot["chatids"]:
                telegram_bot.sendMessage(int(cid), "Richiesta di iscrizione agli alert di manutenzione da parte di: "+msg['from'].get('first_name','Utente')+"\n confermare con il comando /confirm " + str(chat_id))
        waiting_confirmation = True
    
    elif comando == '/unsubme':           # Comando per disiscriversi dagli alert
        telegram_bot.sendMessage(chat_id, "Sei stato disiscritto dagli alert di manutenzione.")
        if str(chat_id) in dicttbot["chatids"]:
            dicttbot["chatids"].remove(str(chat_id))
            with open("tbot.conf", "w") as filetbot:
                json.dump(dicttbot, filetbot, indent=4)
    
    elif comando.startswith('/confirm') and (str(chat_id) in dicttbot["chatids"] or 1051473816) and waiting_confirmation:          # Comando per confermare l'iscrizione agli alert
        parts = comando.split(' ')
        if len(parts) > 1:
            chat_id_waiting_confirmation = parts[1]
            dicttbot["chatids"].append(str(chat_id_waiting_confirmation))
            with open("tbot.conf", "w") as filetbot:
                json.dump(dicttbot, filetbot, indent=4)
            telegram_bot.sendMessage(chat_id, "Iscrizione agli alert di manutenzione confermata.")
            telegram_bot.sendMessage(chat_id_waiting_confirmation, "Iscrizione agli alert di manutenzione confermata.")



# Funzione per la connessione al server MAN
def on_connectMAN(client, userdata, flags, reasone_code, properties):

    if reasone_code == mqtt.CONNACK_ACCEPTED:
        client.subscribe(dict["topic"]["alert"], QOS)
        print("----------------------------------------------")
        print("BOT IOTP in ascolto su MQTT: ",dict["broker"]["host"]+": "+str(dict["broker"]["porta"]))
        print("Iscritto al topic: ",dict["topic"]["alert"])
        print("----------------------------------------------\n")

    else:
        print("Connessione fallita, codice:",reasone_code)

# Decodifica del payload 
def on_messageMAN(client, userdata, msg):
    dato = msg.payload.decode(FORMAT)
    dato_decriptato = cripto.decriptazione(dato)
    print("[DEBUG]: alert ricevuto")
    print("----------------------------------------------\n")
    print("messaggio ricevuto:", dato_decriptato)
    print("----------------------------------------------\n")
    dato_json = json.loads(dato_decriptato)
    
    for chat_id in dicttbot["chatids"]:
        telegram_bot.sendMessage(int(chat_id), "ALERT MANUTENZIONE!\nNave: Rocinante"
                                 "\nCabina: "+str(dato_json["cabina"])+
                                 "\nPonte: "+str(dato_json["ponte"])+
                                 "\nData e Ora: "+str(datetime.fromtimestamp((int(dato_json["alert"]["timestamp"]))).strftime("%d/%m/%Y - %H:%M"))+
                                 "\nAlert: "+str(dato_json["alert"]["soglia"])+
                                 "\nCodice DC: "+str(dato_json["identita_dc"])+
                                 "\nPIN segnale: "+str(dato_json["pin_segnale"])+
                                 "\nManuale: "+str(dato_json["documentazione"]["dms_id"])
                                 )

file = open("manutenzione.conf") 
dict = json.load(file)

filetbot = open("tbot.conf") 
dicttbot = json.load(filetbot)
waiting_confirmation = False

QOS = 0
KEEPALIVE = 60
FORMAT = "utf-8"
subscriberMAN = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
subscriberMAN.on_connect = on_connectMAN
subscriberMAN.on_message = on_messageMAN
subscriberMAN.connect(dict["broker"]["host"], dict["broker"]["porta"], KEEPALIVE)
subscriberMAN.loop_start()

telegram_bot = telepot.Bot(dicttbot["token"])
MessageLoop(telegram_bot, azione).run_as_thread()

print ('Bot in esecuzione...')
while 1:
    try:
        time.sleep(0.1)
    except KeyboardInterrupt:
        print ('\nBot terminato.')
        break