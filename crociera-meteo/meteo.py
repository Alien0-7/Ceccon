'''
Allegro Elena, Morari Elia 
5AI

Script meteo.py (request)
''' 
import requests
import json

# Apro il file
file_api = open("apikey.conf")
dict_api = json.load(file_api)

apiKey = dict_api["apikey"]

citta = input("Inserisci il nome della città che vuoi visualizzare il meteo:\n")

url = f"https://api.openweathermap.org/data/2.5/weather?q={citta}&appid={apiKey}&units=metric"

richiesta = requests.get(url)
dict_dati = richiesta.json()
stato_richiesta = richiesta.status_code

# Controllo che la città sia valida
while(stato_richiesta == 404):
    citta = input("ERRORE: Non esiste la citta inserita!\nReinserire la città:\n")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={citta}&appid={apiKey}&units=metric"
    richiesta = requests.get(url)
    dict_dati = richiesta.json()
    stato_richiesta = richiesta.status_code

# Dati presi dalla richiesta
meteo = dict_dati["weather"][0]["main"]
meteo_descr = dict_dati["weather"][0]["description"]
temperatura = dict_dati["main"]["temp"]
temperatura_max = dict_dati["main"]["temp_max"]
temperatura_min = dict_dati["main"]["temp_min"]
pressione = dict_dati["main"]["pressure"]
umidita = dict_dati["main"]["humidity"]
vento_velocita = dict_dati["wind"]["speed"]


print("--- METEO", citta.upper(),"---")
print("Condizione:", meteo, "\nDescrizione:", meteo_descr, 
      "\nTemperatura attuale:", temperatura, 
      "°C\nTemperatura minima:", temperatura_min, "°C\nTemperatura massima:", temperatura_max, 
      "°C\nPressione:", pressione, "hPa\nUmidità:", umidita, "%\nVelocità del vento:", vento_velocita, "m/s")