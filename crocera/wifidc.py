# CONNESSIONE RETE WIFI CON RASPBERRY PICO W
# SCRIPT DI TEST CON VISUALIZZAZIONI DI STATO
#
# SCRIPT: pico1.py
#
import rp2                    # Funzioni e classi specifiche per RP2040 - Raspberry Pi Pico
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
#
def Disabilita_PowerSaving_Mode(wlan):
    wlan.config(pm = 0xa11140)
#
def Connessione_WiFi(wlan, time_out, ssid, psw, pausa):
   wlan.connect(ssid, psw)
   print("Tentativi (attesa): ", time_out)
   while time_out > 0:
       if wlan.status() < 0 or wlan.status() >= 3:
           break
       time_out = time_out - 1
       print("Tentativo connessione")
       time.sleep(pausa)
       
   # Gestione errore
   if wlan.status() != 3:
        while True:
            Errore_con_lampeggio_led(wlan.status())
   else:
        print('Connessione riuscita')
        status = wlan.ifconfig()
        print(status)
        ip_assegnato = status[0]
        print("IP Pico: ", ip_assegnato)
   return
#
def Errore_con_lampeggio_led(num_lampeggi):
    led = machine.Pin('LED', machine.Pin.OUT)
    for i in range(num_lampeggi):
        led.on()
        time.sleep(.2)
        led.off()
        time.sleep(.2)
    return
#
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