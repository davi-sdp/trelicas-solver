import numpy as np
import math
#import pyqt5
#import matplotlib

alfabeto = {chr(65 + i): i for i in range(26)} #gera o dicionario com as letras e os index delas

coords_x, coords_y, rx, ry, fx, fy, f = [],[],[],[],[],[],[]

def entra(texto, tipo=str):
    while True:
        try:
            valor = tipo(input(texto))

            if valor == "":
                continue

            return valor

        except ValueError:
            print(f"Digite um valor válido do tipo {tipo.__name__}")

n_nos = entra("Quantos nós você quer?: ", int)
n_forcas = entra("Quantas forças existem no esquema?: ", int)

for _ in range(n_forcas):
    f.append(0)
    fx.append(0)
    fy.append(0)

# LOCALIZAÇÕES DOS NÓS
for i in range(0,n_nos):
    letra = list(alfabeto.keys())[i]
    temp_x = entra(f"Coordenada X do ponto {letra} [m]: ", float)
    temp_y = entra(f"Coordenada Y do ponto {letra} [m]: ", float)

    print("\n")

    coords_x.append(temp_x)
    coords_y.append(temp_y)

print(coords_x, coords_y)

print("\n")

for i in range(0,n_forcas):

    #qual nó?
    local = alfabeto[entra(f"Em qual nó a Força {i+1} é aplicada?: ", str)]

    temp_f = entra(f"Intensidade da Força {i+1} [N]: ", float)
    f.insert(local,temp_f)

    angulo = entra(f"Ângulo da Força {i+1} em relação ao eixo X [°]: ", float)

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