# funzione archiviazione nel file richiamata da archivia_iotp.py
def archivia(f, modo, dati):
    with open(f, modo) as file: 
        file.write(dati)