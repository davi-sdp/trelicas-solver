import matplotlib.pyplot as plt
import io
import base64
import math

def generate_truss_diagram(coords_x, coords_y, bars, fx, fy, rx, ry, apoios, bar_forces=None):
    fig, ax = plt.subplots(figsize=(10, 7))

    min_x, max_x = min(coords_x), max(coords_x)
    min_y, max_y = min(coords_y), max(coords_y)
    largura = max_x - min_x
    altura = max_y - min_y
    dim_max = max(largura, altura, 1.0)

    mags_f = [math.sqrt(fx[i]**2 + fy[i]**2) for i in range(len(fx))]
    mags_r = [math.sqrt(rx[i]**2 + ry[i]**2) for i in range(len(rx))]
    max_f_global = max(max(mags_f) if mags_f else 0, max(mags_r) if mags_r else 0, 1e-9)

    tamanho_seta_alvo = dim_max * 0.15
    q_scale = max_f_global / tamanho_seta_alvo if max_f_global > 0 else 1.0

    t_lbl, c_lbl, n_lbl = False, False, False
    for i, (n1, n2) in enumerate(bars):
        color, lbl = 'blue', ""
        if bar_forces and i < len(bar_forces):
            ftype = bar_forces[i]['type']
            if ftype == "Tração":
                color = 'blue'
                if not t_lbl: lbl, t_lbl = "Tração", True
            elif ftype == "Compressão":
                color = 'red'
                if not c_lbl: lbl, c_lbl = "Compressão", True
            else:
                color = 'gray'
                if not n_lbl: lbl, n_lbl = "Esforço Nulo", True
        else:
            if i == 0: lbl = "Barras"

        ax.plot([coords_x[n1], coords_x[n2]], [coords_y[n1], coords_y[n2]],
                color=color, linestyle='-', linewidth=2.5, zorder=2, label=lbl)

    label_ext_usado = False
    label_reac_usado = False

    for i in range(len(coords_x)):
        if fx[i] != 0 or fy[i] != 0:
            lbl = 'Força Ext.' if not label_ext_usado else ""
            ax.quiver(coords_x[i], coords_y[i], fx[i], fy[i],
                      color='red', scale=q_scale, scale_units='xy', angles='xy',
                      width=0.005, headwidth=5, headlength=5,
                      zorder=4, label=lbl)
            label_ext_usado = True

        if rx[i] != 0 or ry[i] != 0:
            lbl = 'Reação' if not label_reac_usado else ""
            ax.quiver(coords_x[i], coords_y[i], rx[i], ry[i],
                      color='green', scale=q_scale, scale_units='xy', angles='xy',
                      width=0.005, headwidth=5, headlength=5,
                      zorder=4, label=lbl)
            label_reac_usado = True

    label_fixo_usado = False
    label_movel_y_usado = False
    label_movel_x_usado = False
    for no_idx, tipo in apoios.items():
        x_ap = coords_x[no_idx]
        y_ap = coords_y[no_idx]
        if tipo == 1:
            lbl = 'Apoio Fixo' if not label_fixo_usado else ""
            ax.plot(x_ap, y_ap, '^', markersize=16, color='darkgreen', zorder=3, label=lbl)
            label_fixo_usado = True
        elif tipo == 2:
            lbl = 'Apoio Móvel (Rolete Y)' if not label_movel_y_usado else ""
            ax.plot(x_ap, y_ap, 'o', markersize=12, color='darkgreen', zorder=3,
                    markerfacecolor='none', markeredgewidth=2, label=lbl)
            label_movel_y_usado = True
        else:
            lbl = 'Apoio Móvel (Rolete X)' if not label_movel_x_usado else ""
            ax.plot(x_ap, y_ap, 's', markersize=12, color='darkgreen', zorder=3,
                    markerfacecolor='none', markeredgewidth=2, label=lbl)
            label_movel_x_usado = True

    for i in range(len(coords_x)):
        ax.plot(coords_x[i], coords_y[i], 'ko', markersize=6, zorder=5)
        ax.text(coords_x[i] + 0.05, coords_y[i] + 0.1, chr(65 + i), fontsize=12, fontweight='bold')

    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_title("Esquema da Treliça", fontsize=14)
    ax.set_xlabel("Coordenada X [m]")
    ax.set_ylabel("Coordenada Y [m]")

    padding = tamanho_seta_alvo * 1.5
    ax.set_xlim(min_x - padding, max_x + padding)
    ax.set_ylim(min_y - padding, max_y + padding)
    ax.set_aspect('equal', adjustable='box')
    ax.legend()
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')
