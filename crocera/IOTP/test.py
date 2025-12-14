import serial
import time

ser = serial.Serial('COM4', 9600, timeout=0.1)

while True:
    # invia messaggio
    ser.write(b'getTempHum\n')

    # legge la risposta
    if ser.in_waiting:
        line = ser.readline().decode().strip()
        print("Ricevuto dal micro:bit:", line)
    