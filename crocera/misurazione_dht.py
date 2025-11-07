# DA ESEGUIRE USANDO L'ESTENSIONE MicroPico su visual studio code

import time
from machine import Pin
import dht

INTERVALLO = 5
PIN_SEGNALE = 0
def leggi():
    #sensor = dht.DHT22(Pin(PIN_SEGNALE))  # per il sensore bianco
    sensor = dht.DHT11(Pin(PIN_SEGNALE))
    temp, hum = None, None

    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
    
    except OSError as e:
        print('Problemi con il sensore...')

    return temp, hum