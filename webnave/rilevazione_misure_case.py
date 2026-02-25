# IoT
# 
# Generatore misure casuali per le case
# Numero stanze 8 - DC 8 - piani 1
# Numero case 4
#
# Modulo locale per altri script
# Dati in formato JSON
#
# Script rilevazione_misure_case.py
#
import json
import random
from datetime import datetime
#
def temp(N):
    TEMP = round(random.uniform(10,35), N)
    return TEMP

def umi(N):
    UMI = round(random.uniform(30,70), N)
    return UMI

def dc():
    DC = "DC00" + str(CASA[-1:]) + "-0"  # randint estremi compresi + str(CAMERA)
    return DC

def case():
    global CASA
    CASA = "GIOT-00" + str(random.randint(1,3))
    return CASA
def camere():
    global CAMERA
    CAMERA = random.randint(1,8)
    return CAMERA
def piani():
    PIANO = random.randint(1,1)
    return PIANO

"""
Dato IoT:

{
    "invionumero": 1, 
    "camera": 1,
    "piano": 1,
    "temperaturam": 19.12,
    "umiditam": 64.20,
    "dataeora": 1727283213.159446,
    "casa": "GIOT-001",
    "dc": "DC001-01"
}

"""
def osservazione():
    dizionario={}
    current_datetime = datetime.now()
    ts = current_datetime.timestamp()
    cam = camere()
    tempm = temp(2)
    umim = umi(2)

    dizionario = {'camera':cam,"piano": piani(),'temperaturam':tempm,'umiditam':umim,
                "dataeora":ts,'casa':case(),'dc':dc()}
    # 
    dato_iot_json = json.dumps(dizionario, indent = 4)
    print ("Misure provenienti dalle diverse case")
    print (dato_iot_json)
    print ()
    return dato_iot_json
#
# Nicola Ceccon - laboratorio LTR
# Febbraio 2025
# enneci www.enneci.cloud
# Licenza CC BY-NC
