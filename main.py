import numpy as np
import math
from utils import entra, alfabeto, verificar_intersecao, obter_equacao_reta

coords_x, coords_y = [], []
rx, ry = [], []
fx, fy = [], []
f_res = []

n_nos = entra("Quantos nós você quer?: ", int)
n_forcas = entra("Quantas forças existem no esquema?: ", int)

# Inicializamos as forças com zero para cada nó
for _ in range(n_nos):
    fx.append(0.0)
    fy.append(0.0)
    rx.append(0.0)
    ry.append(0.0)

# LOCALIZAÇÕES DOS NÓS
for i in range(0,n_nos):
    letra = list(alfabeto.keys())[i]
    temp_x = entra(f"Coordenada X do ponto {letra} [m]: ", float)
    temp_y = entra(f"Coordenada Y do ponto {letra} [m]: ", float)

    print("\n")

    coords_x.append(temp_x)
    coords_y.append(temp_y)

print(f"Coordenadas X: {coords_x}")
print(f"Coordenadas Y: {coords_y}\n")

# --- ENTRADA DE FORÇAS ---
for i in range(0,n_forcas):

    #qual nó?
    nos_disponiveis = ", ".join(list(alfabeto.keys())[:len(coords_x)])
    no_input = entra(f"Em qual nó a Força {i+1} é aplicada? Disponíveis ({nos_disponiveis}): ", str).upper()
    local = alfabeto[no_input]
    temp_f = entra(f"Intensidade da Força {i+1} [N]: ", float)
    f_res.append(temp_f)
    angulo = entra(f"Ângulo da Força {i+1} em relação ao eixo X [°]: ", float)

    # para calcular em radianos, já que as funções trigonométricas do math usam radianos
    rad = math.radians(angulo)

    fx[local] += round(math.cos(rad) * temp_f, 10) # precisão de 10 casas
    fy[local] += round(math.sin(rad) * temp_f, 10)

    print("\n")

# --- ENTRADA DE BARRAS (ELEMENTOS) ---
n_barras = entra("Quantas barras existem no esquema?: ", int)
barras = [] # Lista de tuplas (índice_nó1, índice_nó2)

for i in range(n_barras):
    print(f"Definindo Barra {i+1}:")
    n1 = alfabeto[entra("  Nó de origem: ", str).upper()]
    n2 = alfabeto[entra("  Nó de destino: ", str).upper()]
    
    # Verificar cruzamento com barras existentes
    p1 = (coords_x[n1], coords_y[n1])
    p2 = (coords_x[n2], coords_y[n2])
    
    for j, (b_n1, b_n2) in enumerate(barras):
        p3 = (coords_x[b_n1], coords_y[b_n1])
        p4 = (coords_x[b_n2], coords_y[b_n2])
        if verificar_intersecao(p1, p2, p3, p4):
            print(f"ALERTA: A barra {i+1} cruza a barra {j+1}! Revise o projeto.")

    barras.append((n1, n2))
    m, c = obter_equacao_reta(p1, p2)
    if m is None:
        print(f"  Equação da barra: x = {c}")
    else:
        print(f"  Equação da barra: y = {m:.2f}x + {c:.2f}")

# --- ENTRADA DE APOIOS ---
print("\n--- Configuração de Apoios ---")
apoios = {} # {índice_nó: tipo} 
# Tipo 1: Fixo (impede X e Y), Tipo 2: Móvel (impede apenas Y)

n_apoios = entra("Quantos nós possuem apoios?: ", int)
for _ in range(n_apoios):
    no_idx = alfabeto[entra("Letra do nó com apoio: ", str).upper()]
    tipo = entra("Tipo de apoio (1-Fixo/Pino, 2-Móvel/Rolete): ", int)
    apoios[no_idx] = tipo

# --- CÁLCULO DE REAÇÕES (SISTEMA ISOSTÁTICO) ---
indices_apoios = list(apoios.keys())
if len(indices_apoios) >= 2:
    # Identificar nó do apoio fixo (A) e móvel (B)
    no_fixo = [n for n, t in apoios.items() if t == 1][0]
    no_movel = [n for n, t in apoios.items() if t == 2][0]

    x0, y0 = coords_x[no_fixo], coords_y[no_fixo]
    x1, y1 = coords_x[no_movel], coords_y[no_movel]

    # 1. Somatória de Momentos em relação ao apoio fixo (ΣM_A = 0)
    # Momento_Ext + Ry_B * (x1 - x0) = 0
    momento_externo = 0
    for i in range(n_nos):
        dx = coords_x[i] - x0
        dy = coords_y[i] - y0
        momento_externo += (dx * fy[i]) - (dy * fx[i])

    # Reação Vertical no Apoio Móvel (Ry_B)
    dist_x = x1 - x0
    if dist_x != 0:
        ry[no_movel] = -momento_externo / dist_x
    
    # 2. Somatória de Forças em X (ΣFx = 0)
    # Rx_A + Σfx = 0
    rx[no_fixo] = -sum(fx)

    # 3. Somatória de Forças em Y (ΣFy = 0)
    # Ry_A + Ry_B + Σfy = 0
    ry[no_fixo] = -sum(fy) - ry[no_movel]

    print("\nReações Calculadas:")
    print(f"  Nó {list(alfabeto.keys())[no_fixo]} (Fixo): Rx = {rx[no_fixo]:.2f}N, Ry = {ry[no_fixo]:.2f}N")
    print(f"  Nó {list(alfabeto.keys())[no_movel]} (Móvel): Ry = {ry[no_movel]:.2f}N")

# --- VISUALIZAÇÃO (MATPLOTLIB) ---
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
# Desenhar Barras
for n1, n2 in barras:
    plt.plot([coords_x[n1], coords_x[n2]], [coords_y[n1], coords_y[n2]], 'b-', linewidth=2)

# Desenhar Forças (Vetores)
max_f = max(f_res) if f_res else 1
scale_val = max_f * 5

for i in range(n_nos):
    # Forças Externas (Vermelho)
    if fx[i] != 0 or fy[i] != 0:
        plt.quiver(coords_x[i], coords_y[i], fx[i], fy[i], color='r', scale=scale_val, label='Força Ext.' if i==0 else "")
    # Reações (Verde)
    if rx[i] != 0 or ry[i] != 0:
        plt.quiver(coords_x[i], coords_y[i], rx[i], ry[i], color='g', scale=scale_val, label='Reação' if i==0 else "")

# Desenhar Apoios
for no, tipo in apoios.items():
    marker = '^' if tipo == 1 else 'o'
    plt.plot(coords_x[no], coords_y[no], marker, markersize=15, color='green')

plt.grid(True)
plt.title("Esquema da Treliça")
plt.show()