import numpy as np

def solve_truss(nodes, bars, forces, supports, E=29000.0, A=5.0):
    n_nos = len(nodes)

    coords_x = [n['x'] for n in nodes]
    coords_y = [n['y'] for n in nodes]

    F = np.zeros(n_nos * 2)
    for f in forces:
        idx = f['node']
        F[2 * idx] += f['fx']
        F[2 * idx + 1] += f['fy']

    K_g = np.zeros((n_nos * 2, n_nos * 2))

    for n1, n2 in bars:
        dx = coords_x[n2] - coords_x[n1]
        dy = coords_y[n2] - coords_y[n1]
        L = np.hypot(dx, dy)
        if L < 1e-12:
            continue
        c = dx / L
        s = dy / L
        k = E * A / L
        ke = k * np.array([
            [c * c, c * s, -c * c, -c * s],
            [c * s, s * s, -c * s, -s * s],
            [-c * c, -c * s, c * c, c * s],
            [-c * s, -s * s, c * s, s * s]
        ])
        dofs = [2 * n1, 2 * n1 + 1, 2 * n2, 2 * n2 + 1]
        K_g[np.ix_(dofs, dofs)] += ke

    GL = np.arange(n_nos * 2)
    GL_r = []
    for idx_no, tipo in supports.items():
        if tipo == 1:
            GL_r += [2 * idx_no, 2 * idx_no + 1]
        elif tipo == 2:
            GL_r += [2 * idx_no]
        elif tipo == 3:
            GL_r += [2 * idx_no + 1]
    GL_r = sorted(set(GL_r))
    GL_l = np.delete(GL, GL_r)

    K_gr = K_g[np.ix_(GL_l, GL_l)]
    F_r = F[GL_l]
    D_l = np.linalg.solve(K_gr, F_r)

    D_g = np.zeros(n_nos * 2)
    D_g[GL_l] = D_l

    Q = K_g @ D_g
    R = Q - F

    reactions = {}
    for idx_no, tipo in supports.items():
        r = {}
        if tipo == 1:
            r['Rx'] = float(round(R[2 * idx_no], 6))
            r['Ry'] = float(round(R[2 * idx_no + 1], 6))
        elif tipo == 2:
            r['Rx'] = float(round(R[2 * idx_no], 6))
        elif tipo == 3:
            r['Ry'] = float(round(R[2 * idx_no + 1], 6))
        reactions[idx_no] = r

    bar_forces = []
    for n1, n2 in bars:
        dx = coords_x[n2] - coords_x[n1]
        dy = coords_y[n2] - coords_y[n1]
        L = np.hypot(dx, dy)
        if L < 1e-12:
            bar_forces.append({'f': 0.0, 'type': 'Nula'})
            continue
        c = dx / L
        s = dy / L
        dofs = [2 * n1, 2 * n1 + 1, 2 * n2, 2 * n2 + 1]
        q = (E * A / L) * np.dot([c, s, -c, -s], D_g[dofs])
        if abs(q) < 1e-6:
            bar_forces.append({'f': 0.0, 'type': 'Nula'})
        elif q > 0:
            bar_forces.append({'f': round(abs(q), 6), 'type': 'Tração'})
        else:
            bar_forces.append({'f': round(abs(q), 6), 'type': 'Compressão'})

    total_fx_applied = sum(F[2 * i] for i in range(n_nos))
    total_fy_applied = sum(F[2 * i + 1] for i in range(n_nos))
    total_rx = sum(R[i] for i in GL_r if i % 2 == 0)
    total_ry = sum(R[i] for i in GL_r if i % 2 == 1)
    sum_fx = total_fx_applied + total_rx
    sum_fy = total_fy_applied + total_ry
    equilibrium_ok = abs(sum_fx) < 1e-6 and abs(sum_fy) < 1e-6

    return {
        'reactions': reactions,
        'equilibrium_fx': round(float(sum_fx), 6),
        'equilibrium_fy': round(float(sum_fy), 6),
        'equilibrium_ok': bool(equilibrium_ok),
        'message': '',
        'fx': [float(F[2 * i]) for i in range(n_nos)],
        'fy': [float(F[2 * i + 1]) for i in range(n_nos)],
        'rx': [float(R[2 * i]) for i in range(n_nos)],
        'ry': [float(R[2 * i + 1]) for i in range(n_nos)],
        'coords_x': coords_x,
        'coords_y': coords_y,
        'apoios': supports,
        'bar_forces': bar_forces
    }
