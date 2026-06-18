import numpy as np
import math
from utils import calcular_momentos, verificar_intersecao, No, Braco, Forca

def solve_truss_reactions(nodes_data, bars_data, forces_data, supports_data):
    """
    Calcula as reações de apoio para uma treliça isostática.
    Args:
        nodes_data (list): Lista de dicionários com {'x': float, 'y': float} para cada nó.
        bars_data (list): Lista de tuplas (idx_no1, idx_no2) para cada barra.
        forces_data (list): Lista de dicionários com {'magnitude': float, 'angle': float, 'node': int}.
        supports_data (dict): Dicionário {idx_no: tipo_apoio (1=Fixo, 2=Móvel)}.

    Returns:
        dict: Contém 'reactions' (dicionário de reações por nó),
              'equilibrium_fx', 'equilibrium_fy', 'equilibrium_ok',
              'message' (se houver avisos/erros), e os vetores de forças e reações.
    """
    n_nos = len(nodes_data)
    
    # Precisão padrão para arredondamentos
    PRECISAO = 6

    # Instanciação dos objetos (Requisito de POO e organização)
    nos_obj = [No(i, n['x'], n['y'], supports_data.get(i)) for i, n in enumerate(nodes_data)]
    bracos_obj = [Braco(i, nos_obj[b[0]], nos_obj[b[1]]) for i, b in enumerate(bars_data)]
    forcas_obj = [Forca(i, f['magnitude'], f['angle'], f['node']) for i, f in enumerate(forces_data)]

    coords_x = [n.x for n in nos_obj]
    coords_y = [n.y for n in nos_obj]

    # Inicializa vetores de forças e reações
    fx = [0.0] * n_nos
    fy = [0.0] * n_nos
    rx = [0.0] * n_nos
    ry = [0.0] * n_nos
    f_res = [f.magnitude for f in forces_data] # Intensidade das forças externas
    bar_forces = []

    # Processa as forças usando os objetos Forca
    for f in forcas_obj:
        fx[f.no_idx] += round(f.fx, PRECISAO)
        fy[f.no_idx] += round(f.fy, PRECISAO)

    apoios_fixos = [n for n, t in supports_data.items() if t == 1]
    apoios_moveis = [n for n, t in supports_data.items() if t == 2]

    reactions_output = {}
    message = ""
    
    # Verificação de cruzamento de barras (Requisito de Projeto)
    cruzamentos = []
    for i in range(len(bracos_obj)):
        for j in range(i + 1, len(bracos_obj)):
            p1, p2 = (bracos_obj[i].no1.x, bracos_obj[i].no1.y), (bracos_obj[i].no2.x, bracos_obj[i].no2.y)
            p3, p4 = (bracos_obj[j].no1.x, bracos_obj[j].no1.y), (bracos_obj[j].no2.x, bracos_obj[j].no2.y)
            if verificar_intersecao(p1, p2, p3, p4):
                cruzamentos.append(f"Barras {i+1} e {j+1}")
    
    if cruzamentos:
        message += "AVISO: As seguintes barras estão se cruzando: " + ", ".join(cruzamentos) + ". "

    equilibrium_fx = 0
    equilibrium_fy = 0
    equilibrium_ok = False

    if len(apoios_fixos) == 1 and len(apoios_moveis) == 1:
        nf = apoios_fixos[0]   # índice do nó fixo
        nm = apoios_moveis[0]  # índice do nó móvel

        soma_fx = sum(fx)
        soma_fy = sum(fy)

        # ΣM em torno do apoio fixo = 0 -> resolve Ry do móvel
        # O momento resultante das forças externas em relação ao apoio fixo deve ser equilibrado pela reação do apoio móvel
        todos_momentos = calcular_momentos(fx, fy, coords_x, coords_y)
        momentos_externos_em_fixo = todos_momentos[nf]

        # Braço de alavanca: distância horizontal entre o apoio móvel e o fixo
        dx_movel = coords_x[nm] - coords_x[nf]
        # dy_movel = coords_y[nm] - coords_y[nf] # Não usado para Ry vertical

        if abs(dx_movel) < 1e-6: # Usar uma tolerância para comparação com zero
            message = "ERRO: Os dois apoios estão alinhados verticalmente. Estrutura instável para cargas verticais."
            equilibrium_ok = False
        else:
            # Calcula a reação vertical no apoio móvel (Ry_movel * dx = -Momento_externo)
            ry[nm] = round(-momentos_externos_em_fixo / dx_movel, PRECISAO)

            # ΣFy = 0 -> Ry_fixo = -ΣFy - Ry_movel
            ry[nf] = round(-soma_fy - ry[nm], PRECISAO)

            # ΣFx = 0 -> Rx_fixo = -ΣFx
            rx[nf] = round(-soma_fx, PRECISAO)

            reactions_output[nf] = {'Rx': rx[nf], 'Ry': ry[nf]}
            reactions_output[nm] = {'Ry': ry[nm]}

            # Verificação de segurança: a soma das forças totais deve ser zero
            equilibrium_fx = round(soma_fx + rx[nf], PRECISAO)
            equilibrium_fy = round(soma_fy + ry[nf] + ry[nm], PRECISAO)
            equilibrium_ok = (equilibrium_fx == 0 and equilibrium_fy == 0)

            # CÁLCULO DE ESFORÇOS INTERNOS (Método Matricial dos Nós)
            # Resolve o sistema [A]{f} = {b} onde 'f' são os esforços nas barras
            if equilibrium_ok:
                num_bars = len(bars_data)
                # Matriz de Equilíbrio A: cada nó contribui com duas linhas (Equilíbrio X e Y)
                # Colunas representam as incógnitas (forças em cada barra)
                A_mat = np.zeros((2 * n_nos, num_bars))
                # Vetor de Carga b: forças conhecidas (externas + reações) que devem ser equilibradas pelas barras
                b_vec = np.zeros(2 * n_nos)
                
                for i, braco in enumerate(bracos_obj):
                    n1, n2 = braco.no1.id, braco.no2.id
                    ux, uy = braco.c, braco.s # Usa os cossenos diretores já calculados no objeto
                    
                    # A força da barra 'i' atua nos nós n1 e n2 com direções opostas
                    # No nó de origem (n1):
                    A_mat[2*n1, i], A_mat[2*n1+1, i] = ux, uy
                    # No nó de destino (n2):
                    A_mat[2*n2, i], A_mat[2*n2+1, i] = -ux, -uy
                
                for i in range(n_nos):
                    # O sistema resolve A*f + (Cargas+Reações) = 0, logo A*f = -(Cargas+Reações)
                    b_vec[2*i], b_vec[2*i+1] = -(fx[i] + rx[i]), -(fy[i] + ry[i])
                
                try:
                    # Resolvemos usando Mínimos Quadrados (lstsq) para maior robustez numérica
                    # sol contém os valores das forças nas barras
                    sol, _, _, _ = np.linalg.lstsq(A_mat, b_vec, rcond=None)
                    for val in sol:
                        val = round(float(val), PRECISAO)
                        # Se a força é positiva, a barra está sob tração (puxando o nó)
                        t = "Tração" if val > 1e-6 else ("Compressão" if val < -1e-6 else "Nula")
                        bar_forces.append({'f': abs(val), 'type': t})
                except Exception as e:
                    message += f"Erro no cálculo dos esforços internos: {str(e)}. "

    elif len(apoios_fixos) == 0:
        message = "AVISO: Nenhum apoio fixo definido. Reações não calculadas."
    else:
        message = (f"AVISO: Configuração de apoios não isostática padrão "
                   f"({len(apoios_fixos)} fixo(s), {len(apoios_moveis)} móvel(is)). "
                   f"Reações não calculadas automaticamente.")

    return {
        'reactions': reactions_output,
        'equilibrium_fx': equilibrium_fx,
        'equilibrium_fy': equilibrium_fy,
        'equilibrium_ok': equilibrium_ok,
        'message': message,
        'fx': fx,
        'fy': fy,
        'rx': rx,
        'ry': ry,
        'coords_x': coords_x,
        'coords_y': coords_y,
        'f_res': f_res,
        'apoios': supports_data,
        'bar_forces': bar_forces
    }