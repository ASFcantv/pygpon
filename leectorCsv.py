import csv
import numpy



def leer(path):
    results=[]
    with open(path) as File:
        reader = csv.reader(File, delimiter=';')#leer el archivo
    
        for row in reader:
            results.append(row)

    return results
