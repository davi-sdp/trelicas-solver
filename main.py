import numpy as np
import math
from utils import entra, alfabeto, verificar_intersecao, obter_equacao_reta
from tests import test_cases

coords_x, coords_y = [], []
rx, ry = [], []
fx, fy = [], []
f_res = []
apoios = {}

def inicializar_vetores(n):
    for _ in range(n):
        fx.append(0.0)
        fy.append(0.0)
        rx.append(0.0)
        ry.append(0.0)

usando_teste = False
test = entra("Deseja usar um caso de teste? (s/n): ", str).lower()
if test == 's':
    print("\nCasos de Teste Disponíveis:")
    for idx, case in enumerate(test_cases):
        print(f"{idx+1}. {case['name']}")
    
    escolha = entra("Escolha um caso de teste pelo número: ", int) - 1
    if 0 <= escolha < len(test_cases):
        caso = test_cases[escolha]
        n_nos = caso['n_nos']
        n_forcas = caso['n_forcas']
        n_barras = caso['n_barras']
        n_apoios = caso['n_apoios']
        print(f"\nCarregando {caso['name']} com {n_nos} nós, {n_forcas} forças, {n_barras} barras e {n_apoios} apoios.\n")
        
        # Preenchendo as estruturas de dados com as informações do teste
        inicializar_vetores(n_nos)
        for x, y in caso['coords']:
            coords_x.append(x)
            coords_y.append(y)
            
        for val_x, val_y, no_ref in caso['forcas']:
            idx = no_ref - 1 # Converte para índice 0
            fx[idx] += float(val_x)
            fy[idx] += float(val_y)
            f_res.append(math.sqrt(val_x**2 + val_y**2))
            
        barras = [(b1-1, b2-1) for b1, b2 in caso['barras']]
        apoios = {no-1: tipo for no, tipo in caso['apoios'].items()}
        usando_teste = True
    else:
        print("Escolha inválida. Iniciando entrada manual.\n")
else:
    print("\nIniciando entrada manual...\n")

if not usando_teste:
    n_nos = entra("Quantos nós você quer?: ", int)
    n_forcas = entra("Quantas forças existem no esquema?: ", int)
    inicializar_vetores(n_nos)

# =========================================================================================
# onde estão os nós? (coordenadas)
if not usando_teste:
    for i in range(0,n_nos):
        letra = list(alfabeto.keys())[i]
        print(f"\nDefinindo Nó {letra}:")
        temp_x = entra(f"Coordenada X do ponto {letra} [m]: ", float)
        temp_y = entra(f"Coordenada Y do ponto {letra} [m]: ", float)
        print("\n")
        coords_x.append(temp_x)
        coords_y.append(temp_y)

print(f"Coordenadas X: {coords_x}")
print(f"Coordenadas Y: {coords_y}\n")

# =========================================================================================
# Quais são as forças? (intensidade, direção e ponto de aplicação)
if not usando_teste:
    for i in range(0,n_forcas):
        nos_disponiveis = ", ".join(list(alfabeto.keys())[:len(coords_x)])
        no_input = entra(f"Em qual nó a Força {i+1} é aplicada? Disponíveis ({nos_disponiveis}): ", str).upper()
        local = alfabeto[no_input]
        temp_f = entra(f"Intensidade da Força {i+1} [N]: ", float)
        f_res.append(temp_f)
        angulo = entra(f"Ângulo da Força {i+1} em relação ao eixo X [°]: ", float)

        rad = math.radians(angulo)
        fx[local] += round(math.cos(rad) * temp_f, 10)
        fy[local] += round(math.sin(rad) * temp_f, 10)
        print("\n")

# =========================================================================================
# --- ENTRADA DE BARRAS (ELEMENTOS) ---
if not usando_teste:
    n_barras = entra("Quantas barras existem no esquema?: ", int)
    barras = [] # Lista de tuplas (índice_nó1, índice_nó2)

for i in range(n_barras):
    if not usando_teste:
        print(f"Definindo Barra {i+1}:")
        n1 = alfabeto[entra("  Nó de origem: ", str).upper()]
        n2 = alfabeto[entra("  Nó de destino: ", str).upper()]
        barras.append((n1, n2))
    else:
        n1, n2 = barras[i]
    
    # Verificar cruzamento com barras existentes
    p1 = (coords_x[n1], coords_y[n1])
    p2 = (coords_x[n2], coords_y[n2])
    
    for j, (b_n1, b_n2) in enumerate(barras[:i]):
        p3 = (coords_x[b_n1], coords_y[b_n1])
        p4 = (coords_x[b_n2], coords_y[b_n2])
        # nenhuma barra pode cruzar outra, só se compartilharem um nó (o que é permitido)
        if verificar_intersecao(p1, p2, p3, p4):
            print(f"ALERTA: A barra {i+1} cruza a barra {j+1}! Revise o projeto.")

    m, c = obter_equacao_reta(p1, p2)
    if m is None:
        print(f"  Equação da barra: x = {c}")
    else:
        print(f"  Equação da barra: y = {m:.2f}x + {c:.2f}")

# =========================================================================================
# Entrada dos tipos de apoio
if not usando_teste:
    print("\n--- Configuração de Apoios ---")
    n_apoios = entra("Quantos nós possuem apoios?: ", int)
    for _ in range(n_apoios):
        no_idx = alfabeto[entra("Letra do nó com apoio: ", str).upper()]
        tipo = entra("Tipo de apoio (1-Fixo/Pino, 2-Móvel/Rolete): ", int)
        apoios[no_idx] = tipo

# =========================================================================================
# --- CÁLCULO DE REAÇÕES (SISTEMA ISOSTÁTICO) ---
indices_apoios = list(apoios.keys())

# Identificar nó do apoio fixo (tipo 1) e móvel (tipo 2)
apoios_fixos = [n for n, t in apoios.items() if t == 1]
apoios_moveis = [n for n, t in apoios.items() if t == 2]

if len(apoios_fixos) > 0 and len(apoios_moveis) > 0:
    no_fixo = apoios_fixos[0]
    no_movel = apoios_moveis[0]

    x0, y0 = coords_x[no_fixo], coords_y[no_fixo]
    x1, y1 = coords_x[no_movel], coords_y[no_movel]

    # 1. Somatória de Momentos em relação ao apoio fixo (ΣM_A = 0)
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
    rx[no_fixo] = -sum(fx)

    # 3. Somatória de Forças em Y (ΣFy = 0)
    ry[no_fixo] = -sum(fy) - ry[no_movel]

    print("\nReações Calculadas:")
    print(f"  Nó {list(alfabeto.keys())[no_fixo]} (Fixo): Rx = {rx[no_fixo]:.2f}N, Ry = {ry[no_fixo]:.2f}N")
    print(f"  Nó {list(alfabeto.keys())[no_movel]} (Móvel): Ry = {ry[no_movel]:.2f}N")
else:
    print("\n[Aviso] Reações não puderam ser calculadas.")
    print("O sistema requer pelo menos um apoio Fixo (1) e um Móvel (2).")

# =========================================================================================
# --- MATPLOTINHO ---
import matplotlib.pyplot as plt

# configurar limites do gráfico
x_max = max(coords_x) + 1
y_max = max(coords_y) + 1
x_min = min(coords_x) - 1
y_min = min(coords_y) - 1

plt.figure(figsize=(10, 6))
# Desenhar Barras
for n1, n2 in barras:
    plt.plot([coords_x[n1], coords_x[n2]], [coords_y[n1], coords_y[n2]], 'b-', linewidth=2)

# Desenhar Forças (Vetores)
max_f = max(f_res) if f_res and max(f_res) > 0 else 1
scale_val = 5  # Valor fixo de escala para melhor visualização

for i in range(n_nos):
    # Forças Externas (Vermelho)
    if fx[i] != 0 or fy[i] != 0:
        plt.quiver(coords_x[i], coords_y[i], fx[i]/max_f, fy[i]/max_f, color='r', scale=scale_val, label='Força Ext.' if i==0 else "")
    # Reações (Verde)
    if rx[i] != 0 or ry[i] != 0:
        plt.quiver(coords_x[i], coords_y[i], rx[i]/max_f, ry[i]/max_f, color='g', scale=scale_val, label='Reação' if i==0 else "")

# Desenhar Apoios
for no, tipo in apoios.items():
    # tringulo pro fixo, círculo pro móvel
    if tipo == 1:
        marker = '^' 
    else:
        marker = 'o'
    plt.plot(coords_x[no], coords_y[no]-(coords_y[no]*0.1), marker, markersize=15, color='green')

for i in range(n_nos):
    letra = list(alfabeto.keys())[i]
    plt.text(coords_x[i], coords_y[i], f" {letra}", fontsize=12, verticalalignment='bottom', horizontalalignment='right')
    plt.plot(coords_x[i], coords_y[i], 'ko', markersize=5)  # Nó como ponto preto

if caso['chao']:
    plt.axhline(0, color='gray', linestyle='--', linewidth=1)

plt.grid(True)
plt.title("Esquema da Treliça")
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.xlabel("Coordenada X [m]")
plt.ylabel("Coordenada Y [m]")
plt.legend()
ax = plt.gca()
ax.set_aspect('equal', adjustable='box')
plt.show()