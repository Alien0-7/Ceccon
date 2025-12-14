'''
Allegro Elena, Morari Elia 
5AI

Script archivia.py
Funzione archiviazione nel file richiamata da archivia_iotp.py
'''

def archivia(f, modo, dati):
    with open(f, modo) as file: 
        file.write(dati+"\n")