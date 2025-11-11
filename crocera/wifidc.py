'''
Allegro Elena, Morari Elia 
5AI

Script wifidc.py 
'''
import network
import ubinascii              # Conversions between binary data and various encodings of it in ASCII form
import machine                # Funzioni relative all'HW utilizzato
import time
#
def Parametri_WiFi():
    import json
    with open('wifipico.json', 'r') as file:
        credenziali = json.load(file)
        ssid = credenziali["ssid"]
        pasw = credenziali["pw"]
    return ssid,pasw

def Disabilita_PowerSaving_Mode(wlan):
    wlan.config(pm = wlan.PM_NONE) # Disabilita Power Saving Mode per migliorare la stabilità della connessione WiFi

def Connessione_WiFi(wlan, time_out, ssid, psw, pausa):
    wlan.connect(ssid, psw)
    print("Tentativi (attesa):", time_out)
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
            Errore_con_lampeggio_led(wlan.status())
    else:
        print('Connessione riuscita')
        status = wlan.ifconfig()
        print(status)
        ip_assegnato = status[0]
        print("IP ESP32: ", ip_assegnato)

def Errore_con_lampeggio_led(num_lampeggi):
    led = machine.Pin(2, machine.Pin.OUT)
    for i in range(num_lampeggi):
        led.on()
        time.sleep(.2)
        led.off()
        time.sleep(.2)
    return

def Info_WiFi(wlan):
    mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()  # MAC chip wireless
    print('mac = ' + mac)
    print('Canale: ',wlan.config('channel'))
    print('SSID: ', wlan.config('essid'))
    print('Segnale: ', wlan.config('txpower'))
    print()
    print("Scansione")
    print("(ssid, bssid, channel, RSSI, security, hidden)")
    print(wlan.scan())
    print()
    return