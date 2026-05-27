import numpy as np
import math
#import pyqt5
#import matplotlib

alfabeto = [
    "A", "B", "C", "D", "E", "F", "G",
    "H", "I", "J", "K", "L", "M", "N",
    "O", "P", "Q", "R", "S", "T", "U",
    "V", "W", "X", "Y", "Z"
]

coords_x, coords_y, rx, ry, fx, fy, f = [0],[0],[0],[0],[0],[0],[0]

nos = int(input("Quantos nós você quer?: "))

for i in range(nos,26):
    letra = alfabeto[i - nos]
    temp_x = float(input(f"Coordenada X do ponto {letra}: "))
    temp_y = float(input(f"Coordenada Y do ponto {letra}: "))

    coords_x.append(temp_x)
    coords_y.append(temp_y)


print(coords_x)
print(coords_y)
