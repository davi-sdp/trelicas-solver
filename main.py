import numpy as np
import math
#import pyqt5
#import matplotlib

alfabeto = {chr(65 + i): i for i in range(26)} #gera o dicionario com as letras e os index delas

coords_x, coords_y, rx, ry, fx, fy, f = [],[],[],[],[],[],[]

n_nos = int(input("Quantos nós você quer?: "))
n_forcas = int(input("Quantas forças existem no esquema?: "))

for _ in range(n_forcas):
    f.append(0)
    fx.append(0)
    fy.append(0)

# LOCALIZAÇÕES DOS NÓS
for i in range(0,n_nos):
    letra = list(alfabeto.keys())[i]
    temp_x = float(input(f"Coordenada X do ponto {letra} [m]: "))
    temp_y = float(input(f"Coordenada Y do ponto {letra} [m]: "))

    print("\n")

    coords_x.append(temp_x)
    coords_y.append(temp_y)

print(coords_x, coords_y)

   

print("\n")

for i in range(0,n_forcas):

    #qual nó?
    local = alfabeto[str(input(f"Em qual nó a Força {i+1} é aplicada?: "))]

    temp_f = float(input(f"Intensidade da Força {i+1} [N]: "))
    f.insert(local,temp_f)

    angulo = float(input(f"Ângulo da Força {i+1} em relação ao eixo X [°]: "))

    if angulo == 90:
        fy.insert(local,temp_f)
        fx.insert(local,0)
    elif angulo == 0:
        fx.insert(local,temp_f)
        fy.insert(local,0)
    else:
        fx.insert(local,(math.cos(math.radians(angulo)) * temp_f)) 
        fy.insert(local,(math.sin(math.radians(angulo)) * temp_f))

    print("\n")

print(f, fx, fy)