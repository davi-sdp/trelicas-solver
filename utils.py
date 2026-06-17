import math
import sympy
import numpy as np

alfabeto = {chr(65 + i): i for i in range(26)} # gera o dicionario com as letras e os index delas

class No:
    def __init__(self, id, x, y, apoio=None):
        self.id = id
        self.x = x
        self.y = y
        self.apoio = apoio # 1 para pino/fixo, 2 para rolete/móvel

class Braco:
    def __init__(self, id, no1, no2):
        self.id = id
        self.no1 = no1 # Objeto No
        self.no2 = no2 # Objeto No
        self.comprimento = np.hypot(self.no2.x - self.no1.x, self.no2.y - self.no1.y)
        # Usamos atan2 para evitar divisão por zero em barras verticais
        self.angulo = np.arctan2(self.no2.y - self.no1.y, self.no2.x - self.no1.x)
        self.c = np.cos(self.angulo)
        self.s = np.sin(self.angulo)

class Forca:
    def __init__(self, id, magnitude, angulo, no_idx):
        self.id = id
        self.no_idx = no_idx
        self.fx = magnitude * np.cos(np.radians(angulo))
        self.fy = magnitude * np.sin(np.radians(angulo))

def entra(texto, tipo=str):
    """Função utilitária para validar entradas de dados."""
    while True:
        try:
            valor = tipo(input(texto))
            if valor == "":
                continue
            return valor
        except ValueError:
            print(f"Digite um valor válido do tipo {tipo.__name__}\n")

def verificar_intersecao(p1, p2, p3, p4):
    """
    Verifica se o segmento (p1,p2) cruza com (p3,p4) usando o produto vetorial.
    p = (x, y)
    """
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    # Se os segmentos compartilham um nó, não contamos como cruzamento proibido
    if len({p1, p2, p3, p4}) < 4:
        return False

    return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)

def obter_equacao_reta(p1, p2):
    """Retorna m e c para y = mx + c ou (None, x) se vertical."""
    x1, y1 = p1
    x2, y2 = p2
    if x2 - x1 == 0:
        return None, x1
    m = (y2 - y1) / (x2 - x1)
    c = y1 - m * x1
    return m, c

def calcular_momentos(fx, fy, coords_x, coords_y, momentos=None):
    """
    Calcula o momento resultante em cada nó causado pelas forças externas.
    O momento no nó 'j' é a soma dos momentos de todas as forças 'i' em relação a 'j'.
    M = r_x * F_y - r_y * F_x
    Suporta cálculos numéricos e simbólicos (sympy).
    """
    n_nos = len(coords_x)
    if momentos is None or len(momentos) != n_nos:
        momentos = [0.0] * n_nos

    for j in range(n_nos):
        soma_m = 0.0
        for i in range(len(fx)):
            dx = coords_x[i] - coords_x[j] #ditancia em x
            dy = coords_y[i] - coords_y[j] #distancia em y
            soma_m += (dx * fy[i]) - (dy * fx[i]) #formula do momento
        try:
            # arredondando em calculos numerocos
            momentos[j] = round(float(soma_m), 6)
        except (TypeError, ValueError):
            # se for simbolico, mantem a expressão e nao arredonda
            momentos[j] = soma_m
    return momentos

def n_resolver(formula):
    # exemplo de formula: "n*(n-1)/2 - n + 1 = 0"
    """Resolve a fórmula simbólica para n usando sympy."""
    n_sym = sympy.symbols('n')
    resultado = sympy.solve(formula, n_sym)
    if resultado:
        return resultado[0].evalf() # Retorna o valor numérico de n
    else:
        raise ValueError("Não foi possível resolver a fórmula para n.")
    
    return None