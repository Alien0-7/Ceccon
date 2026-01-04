'''
Allegro Elena, Morari Elia 
5AI

Script: cripto.py
Simulazione con sostituzione della lettera 'a' con '*'
'''
def criptazione(payload):
    criptato = payload.replace("a","*")
    return criptato

def decriptazione(payload):
    decriptato = payload.replace("*","a")
    return decriptato
