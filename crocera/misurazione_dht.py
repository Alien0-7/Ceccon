'''
Allegro Elena, Morari Elia 
5AI

Script misurazione_dht.py 
'''
# DA ESEGUIRE USANDO L'ESTENSIONE MicroPico su visual studio code

import time
from machine import Pin   # Modulo per gestire i PIN
import dht                

INTERVALLO = 5
PIN_SEGNALE = 0

# Funzione leggi
def leggi():
    #sensor = dht.DHT22(Pin(PIN_SEGNALE))  # per il sensore bianco
    sensor = dht.DHT11(Pin(PIN_SEGNALE))
    temp, hum = None, None

    try:
        sensor.measure()   # Avvia la misurazione 
        temp = sensor.temperature()  # Temperatura rilevata
        hum = sensor.humidity()      # Umidità rilevata
    
    except OSError as e:
        print('Problemi con il sensore...')

    return temp, hum  # Restituisce la temperatura e l'umidità