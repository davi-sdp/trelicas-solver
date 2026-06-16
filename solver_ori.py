import numpy as np
import math
from utils import entra, alfabeto, verificar_intersecao, obter_equacao_reta, calcular_momentos
from tests import test_cases

coords_x, coords_y = [], []
rx, ry = [], []  # reações nos apoios (calculadas depois)
fx, fy = [], []
f_res = []       # intensidade das forças
apoios = {}      # NÓ: TIPO (1-Fixo/Pino, 2-Móvel/Rolete)
barras = []
momentos = []
usando_teste = False
caso = None

def inicializar_vetores(n):
    for _ in range(n):
        fx.append(0.0)
        fy.append(0.0)
        rx.append(0.0)
        ry.append(0.0)
        momentos.append(0.0)

# =========================================================================================
# ENTRADA DE DADOS
test = entra("Deseja usar um caso de teste? (s/n): ", str).lower()
if test == 's':
    print("\nCasos de Teste Disponíveis:")
    for idx, case in enumerate(test_cases):
        print(f"  {idx+1}. {case['name']}")

    escolha = entra("Escolha um caso de teste pelo número: ", int) - 1
    if 0 <= escolha < len(test_cases):
        caso = test_cases[escolha]
        n_nos    = caso['n_nos']
        n_forcas = caso['n_forcas']
        n_barras = caso['n_barras']
        n_apoios = caso['n_apoios']
        print(f"\nCarregando {caso['name']} com {n_nos} nós, {n_forcas} forças, "
              f"{n_barras} barras e {n_apoios} apoios.\n")

        inicializar_vetores(n_nos)

        for x, y in caso['coords']:
            coords_x.append(x)
            coords_y.append(y)

        for val_x, val_y, no_ref in caso['forcas']:
            idx = no_ref - 1
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
    n_nos    = entra("Quantos nós você quer?: ", int)
    n_forcas = entra("Quantas forças existem no esquema?: ", int)
    inicializar_vetores(n_nos)

# =========================================================================================
# COORDENADAS DOS NÓS
if not usando_teste:
    for i in range(n_nos):
        letra = list(alfabeto.keys())[i]
        print(f"\nDefinindo Nó {letra}:")
        coords_x.append(entra(f"  Coordenada X do ponto {letra} [m]: ", float))
        coords_y.append(entra(f"  Coordenada Y do ponto {letra} [m]: ", float))

print(f"Coordenadas X: {coords_x}")
print(f"Coordenadas Y: {coords_y}\n")

# =========================================================================================
# FORÇAS EXTERNAS
if not usando_teste:
    for i in range(n_forcas):
        nos_disponiveis = ", ".join(list(alfabeto.keys())[:n_nos])
        while True:
            no_input = entra(f"Em qual nó a Força {i+1} é aplicada? ({nos_disponiveis}): ", str).upper()
            if no_input in alfabeto and alfabeto[no_input] < n_nos:
                local = alfabeto[no_input]
                break
            print(f"Erro: Nó '{no_input}' inválido. Escolha entre: {nos_disponiveis}")

        temp_f = entra(f"Intensidade da Força {i+1} [N]: ", float)
        f_res.append(temp_f)
        angulo = entra(f"Ângulo da Força {i+1} em relação ao eixo X [°]: ", float)

        rad = math.radians(angulo)
        fx[local] += round(math.cos(rad) * temp_f, 10)
        fy[local] += round(math.sin(rad) * temp_f, 10)

print(f"Forças em X: {fx}")
print(f"Forças em Y: {fy}\n")

# =========================================================================================
# BARRAS (ELEMENTOS)
if not usando_teste:
    n_barras = entra("Quantas barras existem no esquema?: ", int)

for i in range(n_barras):
    if not usando_teste:
        nos_disponiveis = ", ".join(list(alfabeto.keys())[:n_nos])
        print(f"Definindo Barra {i+1}:")
        while True:
            origem  = entra("  Nó de origem: ", str).upper()
            destino = entra("  Nó de destino: ", str).upper()
            if (origem in alfabeto and alfabeto[origem] < n_nos and
                    destino in alfabeto and alfabeto[destino] < n_nos):
                n1, n2 = alfabeto[origem], alfabeto[destino]
                if n1 != n2:
                    break
                print("Erro: O nó de origem não pode ser igual ao de destino.")
            else:
                print(f"Erro: Use letras dos nós disponíveis: {nos_disponiveis}")
        barras.append((n1, n2))
    else:
        n1, n2 = barras[i]

    p1 = (coords_x[n1], coords_y[n1])
    p2 = (coords_x[n2], coords_y[n2])

    for j, (b_n1, b_n2) in enumerate(barras[:i]):
        p3 = (coords_x[b_n1], coords_y[b_n1])
        p4 = (coords_x[b_n2], coords_y[b_n2])
        if verificar_intersecao(p1, p2, p3, p4):
            print(f"  ALERTA: Barra {i+1} cruza a barra {j+1}! Revise o projeto.")

    m, c = obter_equacao_reta(p1, p2)
    if m is None:
        print(f"  Equação da barra {i+1}: x = {c}")
    else:
        print(f"  Equação da barra {i+1}: y = {m:.2f}x + {c:.2f}")

# =========================================================================================
# CONFIGURAÇÃO DE APOIOS
if not usando_teste:
    print("\n--- Configuração de Apoios ---")
    n_apoios = entra("Quantos nós possuem apoios?: ", int)
    nos_disponiveis = ", ".join(list(alfabeto.keys())[:n_nos])
    for _ in range(n_apoios):
        while True:
            no_input = entra("Letra do nó com apoio: ", str).upper()
            if no_input in alfabeto and alfabeto[no_input] < n_nos:
                no_idx = alfabeto[no_input]
                break
            print(f"Erro: Nó '{no_input}' inválido. Disponíveis: {nos_disponiveis}")
        tipo = entra("Tipo de apoio (1-Fixo/Pino, 2-Móvel/Rolete): ", int)
        apoios[no_idx] = tipo

# =========================================================================================
# CÁLCULO DE REAÇÕES (SISTEMA ISOSTÁTICO)
# Para ser isostático: 1 apoio fixo (Rx + Ry) + 1 apoio móvel (Ry) = 3 incógnitas = 3 equações
apoios_fixos  = [n for n, t in apoios.items() if t == 1]
apoios_moveis = [n for n, t in apoios.items() if t == 2]

if len(apoios_fixos) == 1 and len(apoios_moveis) == 1:
    nf = apoios_fixos[0]   # índice do nó fixo
    nm = apoios_moveis[0]  # índice do nó móvel

    soma_fx = sum(fx)
    soma_fy = sum(fy)

    # ΣM em torno do apoio fixo = 0 -> resolve Ry do móvel
    # M = dx * Fy - dy * Fx  (braço do ponto de aplicação até o apoio fixo)
    m_preliminar = calcular_momentos(fx, fy, coords_x, coords_y)
    momento_externo_em_fixo = m_preliminar[nf]

    # Braço do apoio móvel em relação ao fixo (apenas componente x, pois Ry_movel é vertical)
    dx_movel = coords_x[nm] - coords_x[nf]
    dy_movel = coords_y[nm] - coords_y[nf]

    # O apoio móvel contribui com Ry*dx_movel no momento em torno do fixo
    # Se a barra for inclinada, a reação do rolete é perpendicular à superfície de rolamento
    # Aqui assumimos superfície horizontal → reação vertical
    if abs(dx_movel) < 1e-10:
        # Apoios alinhados verticalmente: a reação do móvel não pode equilibrar momento — estrutura inválida
        print("\nERRO: Os dois apoios estão alinhados verticalmente. Estrutura instável para cargas verticais.")
    else:
        ry[nm] = round(-momento_externo_em_fixo / dx_movel, 6)

        # ΣFy = 0 -> Ry_fixo = -ΣFy - Ry_movel
        ry[nf] = round(-soma_fy - ry[nm], 6)

        # ΣFx = 0 -> Rx_fixo = -ΣFx
        rx[nf] = round(-soma_fx, 6)

        print("\n--- Reações nos Apoios ---")
        letras = list(alfabeto.keys())
        print(f"  Apoio Fixo  [{letras[nf]}]: Rx = {rx[nf]} N  |  Ry = {ry[nf]} N")
        print(f"  Apoio Móvel [{letras[nm]}]: Ry = {ry[nm]} N")

        # Verificação de equilíbrio
        eq_fx = round(soma_fx + rx[nf], 6)
        eq_fy = round(soma_fy + ry[nf] + ry[nm], 6)
        
        # Verificação extra de momento em relação ao nó móvel para garantir consistência
        m_reac_no_movel = (coords_x[nf] - coords_x[nm]) * ry[nf] - (coords_y[nf] - coords_y[nm]) * rx[nf]
        m_ext_no_movel = calcular_momentos(fx, fy, coords_x, coords_y)[nm]
        eq_m = round(m_ext_no_movel + m_reac_no_movel, 6)

        ok = "OK" if eq_fx == 0 and eq_fy == 0 and eq_m == 0 else "✗ PROBLEMA!"
        print(f"\n  Verificação de Equilíbrio:")
        print(f"    ΣFx = {eq_fx} N | ΣFy = {eq_fy} N | ΣM_móvel = {eq_m} N.m  [{ok}]")

elif len(apoios_fixos) == 0:
    print("\nAVISO: Nenhum apoio fixo definido. Reações não calculadas.")
else:
    print(f"\nAVISO: Configuração de apoios não isostática padrão "
          f"({len(apoios_fixos)} fixo(s), {len(apoios_moveis)} móvel(is)). "
          f"Reações não calculadas automaticamente.")

# Momentos em cada nó
momentos = calcular_momentos(fx, fy, coords_x, coords_y, momentos)
print(f"\nMomentos em cada nó: {momentos}")

# =========================================================================================
# VISUALIZAÇÃO
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

x_max = max(coords_x) + 1
y_max = max(coords_y) + 1
x_min = min(coords_x) - 1
y_min = min(coords_y) - 1

# Margem extra embaixo para os símbolos de apoio
y_min -= 0.8

fig, ax = plt.subplots(figsize=(10, 7))

# Barras
for n1, n2 in barras:
    ax.plot([coords_x[n1], coords_x[n2]], [coords_y[n1], coords_y[n2]], 'b-', linewidth=2.5, zorder=2)

# Forças externas e reações
max_f = max(f_res) if f_res and max(f_res) > 0 else 1
scale_val = 5

label_ext_usado  = False
label_reac_usado = False

for i in range(n_nos):
    if fx[i] != 0 or fy[i] != 0:
        lbl = 'Força Ext.' if not label_ext_usado else ""
        ax.quiver(coords_x[i], coords_y[i], fx[i]/max_f, fy[i]/max_f,
                  color='red', scale=scale_val, zorder=4, label=lbl)
        label_ext_usado = True

    if rx[i] != 0 or ry[i] != 0:
        lbl = 'Reação' if not label_reac_usado else ""
        ax.quiver(coords_x[i], coords_y[i], rx[i]/max_f, ry[i]/max_f,
                  color='green', scale=scale_val, zorder=4, label=lbl)
        label_reac_usado = True

# Apoios — offset fixo para não sumir quando y=0
OFFSET_APOIO = 0.3
for no, tipo in apoios.items():
    x_ap = coords_x[no]
    y_ap = coords_y[no] - OFFSET_APOIO
    if tipo == 1:
        ax.plot(x_ap, y_ap, '^', markersize=16, color='darkgreen', zorder=3)
    else:
        ax.plot(x_ap, y_ap, 'o', markersize=12, color='darkgreen', zorder=3,
                markerfacecolor='none', markeredgewidth=2)

# Nós e rótulos
letras = list(alfabeto.keys())
for i in range(n_nos):
    ax.plot(coords_x[i], coords_y[i], 'ko', markersize=6, zorder=5)
    ax.text(coords_x[i] + 0.05, coords_y[i] + 0.1, letras[i], fontsize=12, fontweight='bold')

if usando_teste and caso is not None and caso.get('chao'):
    ax.axhline(0, color='gray', linestyle='--', linewidth=1)

ax.grid(True, linestyle=':', alpha=0.6)
ax.set_title("Esquema da Treliça", fontsize=14)
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.set_xlabel("Coordenada X [m]")
ax.set_ylabel("Coordenada Y [m]")
ax.set_aspect('equal', adjustable='box')
ax.legend()
plt.tight_layout()
plt.show()