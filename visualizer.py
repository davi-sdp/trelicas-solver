import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io
import base64
import math
from utils import alfabeto

def generate_truss_diagram(coords_x, coords_y, bars, fx, fy, rx, ry, apoios, f_res):
    """
    Gera um diagrama da treliça com nós, barras, forças externas e reações.
    Retorna a imagem como uma string base64.
    """
    fig, ax = plt.subplots(figsize=(10, 7))

    # Barras
    for n1, n2 in bars:
        ax.plot([coords_x[n1], coords_x[n2]], [coords_y[n1], coords_y[n2]], 'b-', linewidth=2.5, zorder=2)

    # Forças externas e reações
    max_f = max(f_res) if f_res and max(f_res) > 0 else 1
    scale_val = 0.5 # Ajuste a escala das setas para melhor visualização

    label_ext_usado  = False
    label_reac_usado = False

    for i in range(len(coords_x)):
        # Forças externas
        if fx[i] != 0 or fy[i] != 0:
            # Normaliza a força para o comprimento da seta
            force_magnitude = math.sqrt(fx[i]**2 + fy[i]**2)
            if force_magnitude > 0:
                dx_norm = fx[i] / force_magnitude
                dy_norm = fy[i] / force_magnitude
                lbl = 'Força Ext.' if not label_ext_usado else ""
                ax.quiver(coords_x[i], coords_y[i], dx_norm, dy_norm,
                          color='red', scale=1/scale_val, scale_units='xy', angles='xy', width=0.005, headwidth=5, headlength=5,
                          zorder=4, label=lbl)
                label_ext_usado = True

        # Reações
        if rx[i] != 0 or ry[i] != 0:
            reaction_magnitude = math.sqrt(rx[i]**2 + ry[i]**2)
            if reaction_magnitude > 0:
                dx_norm = rx[i] / reaction_magnitude
                dy_norm = ry[i] / reaction_magnitude
                lbl = 'Reação' if not label_reac_usado else ""
                ax.quiver(coords_x[i], coords_y[i], dx_norm, dy_norm,
                          color='green', scale=1/scale_val, scale_units='xy', angles='xy', width=0.005, headwidth=5, headlength=5,
                          zorder=4, label=lbl)
                label_reac_usado = True

    # Apoios — offset fixo para não sumir quando y=0
    OFFSET_APOIO = 0.3
    for no_idx, tipo in apoios.items():
        x_ap = coords_x[no_idx]
        y_ap = coords_y[no_idx] - OFFSET_APOIO
        if tipo == 1: # Fixo/Pino
            ax.plot(x_ap, y_ap, '^', markersize=16, color='darkgreen', zorder=3, label='Apoio Fixo' if no_idx == list(apoios.keys())[0] else "")
        else: # Móvel/Rolete
            ax.plot(x_ap, y_ap, 'o', markersize=12, color='darkgreen', zorder=3,
                    markerfacecolor='none', markeredgewidth=2, label='Apoio Móvel' if no_idx == list(apoios.keys())[0] else "")

    # Nós e rótulos
    letras = list(alfabeto.keys())
    for i in range(len(coords_x)):
        ax.plot(coords_x[i], coords_y[i], 'ko', markersize=6, zorder=5)
        ax.text(coords_x[i] + 0.05, coords_y[i] + 0.1, letras[i], fontsize=12, fontweight='bold')

    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_title("Esquema da Treliça", fontsize=14)
    ax.set_xlabel("Coordenada X [m]")
    ax.set_ylabel("Coordenada Y [m]")
    ax.set_aspect('equal', adjustable='box')
    ax.legend()
    plt.tight_layout()

    # Salva o gráfico em um buffer e o codifica em base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig) # Fecha a figura para liberar memória
    return base64.b64encode(buf.getvalue()).decode('utf-8')