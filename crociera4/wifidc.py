'''
Allegro Elena, Morari Elia 
5AI

Script wifidc.py 
'''
import network
import ubinascii              # Conversions between binary data and various encodings of it in ASCII form
import machine                # Funzioni relative all'HW utilizzato
import time

# Funzione che legge le credenziali del Wifi dal file "wifipico.conf"
def Parametri_WiFi():
    import json
    with open('wifipico.conf', 'r') as file:
        credenziali = json.load(file)
        ssid = credenziali["ssid"]
        pasw = credenziali["pw"]
    return ssid,pasw

# Funzione per disabilitare il risparmio energetico
def Disabilita_PowerSaving_Mode(wlan):
    wlan.config(pm = wlan.PM_NONE) # Disabilita Power Saving Mode per migliorare la stabilità della connessione WiFi

# Funzione che gestisce la connessione alla rete Wifi
def Connessione_WiFi(wlan, time_out, ssid, psw, pausa):
    wlan.connect(ssid, psw)
    print("Tentativi (attesa):", time_out)
    Lampeggio_led(4, 3)
    # Ciclo di attesa connessione
    while time_out > 0:
        if wlan.isconnected():
            break
        time_out = time_out - 1
        print("Tentativo connessione")
        time.sleep(pausa)

   # Gestione errore
    if not(wlan.isconnected()):
        print('Impossibile connettersi alla rete WiFi, errore:', wlan.status())
        while True:
            Lampeggio_led(2, 3) # Il led lampeggia per segnalare l'errore
    else:
        machine.Pin(15, machine.Pin.OUT).on()
        print('Connessione riuscita')
        status = wlan.ifconfig()
        print(status)
        ip_assegnato = status[0]
        print("IP ESP32: ", ip_assegnato)

# Funzione che fa lampeggiare il led per segnalare l'errore
def Lampeggio_led(led, num_lampeggi):
    led = machine.Pin(led, machine.Pin.OUT)
    for i in range(num_lampeggi):
        led.on()
        time.sleep(.2)
        led.off()
        time.sleep(.2)
    return

# Funzione che stampa le informazioni del Wifi
def Info_WiFi(wlan):

    # Lettura del MAC Adress e conversione in formato leggibile
    mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()  # MAC chip wireless
    
    print('mac = ' + mac)
    print('Canale: ',wlan.config('channel'))
    print('SSID: ', wlan.config('essid'))
    print('Segnale: ', wlan.config('txpower'))
    print()
    # Scansione reti Wifi disponibili
    print("Scansione")
    print("(ssid, bssid, channel, RSSI, security, hidden)")
    print(wlan.scan())  # Restituisce la lista delle reti 
    return
