import numpy as np
#import sympy as sp
import matplotlib.pyplot as plt

class No:
    def __init__(self, id, x, y, apoio=None):
        self.id = id
        self.x = x
        self.y = y
        self.apoio = apoio

class Braco:
    def __init__(self, id, no1, no2):
        self.id = id
        self.no1 = nos[no1]
        self.no2 = nos[no2]
        self.comprimento = np.hypot(self.no2.x-self.no1.x,self.no2.y-self.no1.y)
        self.angulo = np.atan((self.no2.y-self.no1.y)/(self.no2.x-self.no1.x))  
        

class Forca:
    def __init__(self, id, no, fx, fy):
        self.id = id
        self.no = nos[no]
        self.fx = fx
        self.fy = fy

nos = {
    0: No(1, 0.0, 0.0, "pino"),
    1: No(2, 1.0, 1.0, None),
    2: No(3, 2, 0, "rolete")
}

bracos = {
    0: Braco(1, 0, 1),
    1: Braco(2, 1, 2),
    2: Braco(3, 0, 2)
}

forcas = {
    0: Forca(1, 1, 0, -1000)
}
#Vetor de forças
F = np.zeros(len(nos) * 2)
for i in range(len(forcas)):
    F[2*forcas[i].no.id-2:2*forcas[i].no.id] = [forcas[i].fx, forcas[i].fy]

# graus de liberdade = 2, Agora determinamos o tamanho da matriz global de rigidze,
#que é uma matriz de tamanho do numero de nos vezes o GL

#Matriz de rigidez global
K_g = np.zeros((len(nos) * 2, len(nos) * 2))

#Vetor de deslocamentos Ex:(u1x,u1y,u2x,u2y)=(0,1,2,3)
GL = np.arange(len(nos) * 2)
GL_r = []
for i in nos:
    if nos[i].apoio == "pino":
        GL_r += [nos[i].id*2-2, nos[i].id*2-1]
    elif nos[i].apoio == "rolete":
        GL_r += [nos[i].id*2-1]
GL_r = sorted(set(GL_r))
GL_l = np.delete(GL, GL_r)
#reacoes de apoio + numero de barras = 2 * o numero de nos
#r+b=2*n
E = 29000
A = 5
# matriz de rigidez elementar e global
for i in bracos:
    c=np.cos(bracos[i].angulo)
    s=np.sin(bracos[i].angulo)
    L= bracos[i].comprimento
    K = E*A/L*np.array([[c**2, c*s, -c**2,-c*s], 
                        [c*s, s**2, -c*s, -s**2],
                        [-c**2, -c*s, c**2, c*s],
                        [-c*s, -s**2, c*s, s**2]])
    MGL = [bracos[i].no1.id*2-2, bracos[i].no1.id*2-1, bracos[i].no2.id*2-2, bracos[i].no2.id*2-1]
    K_g[np.ix_(MGL, MGL)] += K

K_gr = np.delete(np.delete(K_g, GL_r, 0), GL_r, 1)

# matriz estrutural reduzida de forcas
Q_r = np.delete(F, GL_r)

D = np.zeros(len(nos) * 2)
D = np.matmul(np.linalg.inv(K_gr), Q_r)

D_g = np.zeros(len(nos) * 2)
D_g[GL_l] = D

q_i = np.zeros(len(bracos))

for i in bracos:
    c=np.cos(bracos[i].angulo)
    s=np.sin(bracos[i].angulo)
    L= bracos[i].comprimento
    MGL = [bracos[i].no1.id*2-2, bracos[i].no1.id*2-1, bracos[i].no2.id*2-2, bracos[i].no2.id*2-1]
    # Calcular as forcas internas aplicadas nas barras
    q_i[i] = (A*E/L) * np.dot([c, s, -c, -s], D_g[MGL])

Q = np.matmul(K_g, D_g)
print(q_i)
for i in GL_r:
    print(f"Reação de apoio {i}: {Q[i]}")

for i in range(len(bracos)):
    print(f"Força interna na barra {i}: {q_i[i]}")
