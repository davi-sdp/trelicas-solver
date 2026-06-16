import numpy as np
import math
from utils import alfabeto, calcular_momentos

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
    coords_x = [node['x'] for node in nodes_data]
    coords_y = [node['y'] for node in nodes_data]

    # Inicializa vetores de forças e reações
    fx = [0.0] * n_nos
    fy = [0.0] * n_nos
    rx = [0.0] * n_nos
    ry = [0.0] * n_nos
    f_res = [] # Intensidade das forças externas

    # Aplica forças externas
    for force in forces_data:
        idx = force['node']
        magnitude = force['magnitude']
        angle_rad = math.radians(force['angle'])
        fx[idx] += round(math.cos(angle_rad) * magnitude, 10)
        fy[idx] += round(math.sin(angle_rad) * magnitude, 10)
        f_res.append(magnitude)

    apoios_fixos = [n for n, t in supports_data.items() if t == 1]
    apoios_moveis = [n for n, t in supports_data.items() if t == 2]

    reactions_output = {}
    message = ""
    equilibrium_fx = 0
    equilibrium_fy = 0
    equilibrium_ok = False

    if len(apoios_fixos) == 1 and len(apoios_moveis) == 1:
        nf = apoios_fixos[0]   # índice do nó fixo
        nm = apoios_moveis[0]  # índice do nó móvel

        soma_fx = sum(fx)
        soma_fy = sum(fy)

        # ΣM em torno do apoio fixo = 0  →  resolve Ry do móvel
        # Calcula momentos de todas as forças externas em relação ao nó fixo
        momentos_externos_em_fixo = 0.0
        for i in range(n_nos):
            # Apenas forças externas, não reações ainda
            dx = coords_x[i] - coords_x[nf]
            dy = coords_y[i] - coords_y[nf]
            momentos_externos_em_fixo += (dx * fy[i]) - (dy * fx[i])

        # Braço do apoio móvel em relação ao fixo (apenas componente x, pois Ry_movel é vertical)
        dx_movel = coords_x[nm] - coords_x[nf]
        # dy_movel = coords_y[nm] - coords_y[nf] # Não usado para Ry vertical

        if abs(dx_movel) < 1e-6: # Usar uma tolerância para comparação com zero
            message = "ERRO: Os dois apoios estão alinhados verticalmente. Estrutura instável para cargas verticais."
            equilibrium_ok = False
        else:
            ry[nm] = round(-momentos_externos_em_fixo / dx_movel, 6)

            # ΣFy = 0  →  Ry_fixo = -ΣFy - Ry_movel
            ry[nf] = round(-soma_fy - ry[nm], 6)

            # ΣFx = 0  →  Rx_fixo = -ΣFx
            rx[nf] = round(-soma_fx, 6)

            reactions_output[nf] = {'Rx': rx[nf], 'Ry': ry[nf]}
            reactions_output[nm] = {'Ry': ry[nm]}

            # Verificação de equilíbrio
            equilibrium_fx = round(soma_fx + rx[nf], 6)
            equilibrium_fy = round(soma_fy + ry[nf] + ry[nm], 6)
            equilibrium_ok = (equilibrium_fx == 0 and equilibrium_fy == 0)

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
        'apoios': supports_data
    }