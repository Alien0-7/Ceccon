# 
# FLASK NAVE
# Host default IP dell'host (con 127.0.0.1 connessione negata)
# Porta default 5000
#
# Script nave.py
#
from flask import Flask,render_template,request,redirect          # Librerie di Flask
#
app = Flask(__name__)            # Istanza della classe
#
# Route - URL intercettati
#
@app.route('/')   # Decorator to bind a function to a URL /, route di default http://ip_host:5000
                  # Funzione associata alla root route statica
def index():                     
    return render_template('nave_p.html')
#
@app.route('/temporeale')   # Decorator to bind a function to a URL temporeale
def tr():                     
    return render_template('tr.html')
#



app.run(host = '0.0.0.0', debug=True)   # Runs the application on the host development server
#
# LTR - marzo 2025
# enneci www.enneci.cloud
# Licenza CC BY-NC
#
