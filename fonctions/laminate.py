"""
Matrices de rigidité du pli et du stratifié, par la voie cartésienne
(énoncé 2.b ; P2 slides 27 et 41).

Notation de Voigt : {sigma_11, sigma_22, sigma_12} = Q {eps_11, eps_22, gamma_12}.
Le pli k occupe z_{k-1} <= z <= z_k, de z_0 = -h/2 (bas) à z_n = +h/2 (haut).
Un pli d'angle delta a ses fibres tournées de +delta par rapport à l'axe x.
"""

import numpy as np


def ply_compliance(E1, E2, nu12, G12):
    """Matrice de souplesse S du pli dans ses axes : eps = S sigma."""
    return np.array([
        [1.0 / E1,   -nu12 / E1, 0.0],
        [-nu12 / E1,  1.0 / E2,  0.0],
        [0.0,         0.0,       1.0 / G12],
    ])


def ply_stiffness(S):
    """Matrice de rigidité réduite Q du pli : Q = S^-1."""
    return np.linalg.inv(S)


def rotate_stiffness(Q, angles_deg):
    """
    Rigidités Q(delta) des plis tournés des angles delta (P2 slide 27).
    Renvoie un tableau (n, 3, 3) : une matrice par pli.
    """
    delta = np.radians(np.atleast_1d(angles_deg).astype(float))
    c = np.cos(delta)
    s = np.sin(delta)
    Q11, Q12, Q22, Q66 = Q[0, 0], Q[0, 1], Q[1, 1], Q[2, 2]

    # Formules classiques de rotation, case par case, pour tous les plis à la fois
    Qr = np.zeros((delta.size, 3, 3))
    Qr[:, 0, 0] = Q11 * c**4 + 2 * (Q12 + 2 * Q66) * s**2 * c**2 + Q22 * s**4
    Qr[:, 1, 1] = Q11 * s**4 + 2 * (Q12 + 2 * Q66) * s**2 * c**2 + Q22 * c**4
    Qr[:, 0, 1] = (Q11 + Q22 - 4 * Q66) * s**2 * c**2 + Q12 * (s**4 + c**4)
    Qr[:, 2, 2] = (Q11 + Q22 - 2 * Q12 - 2 * Q66) * s**2 * c**2 + Q66 * (s**4 + c**4)
    Qr[:, 0, 2] = (Q11 - Q12 - 2 * Q66) * s * c**3 + (Q12 - Q22 + 2 * Q66) * s**3 * c
    Qr[:, 1, 2] = (Q11 - Q12 - 2 * Q66) * s**3 * c + (Q12 - Q22 + 2 * Q66) * s * c**3

    # Matrices symétriques : on recopie le triangle du haut en bas
    Qr[:, 1, 0] = Qr[:, 0, 1]
    Qr[:, 2, 0] = Qr[:, 0, 2]
    Qr[:, 2, 1] = Qr[:, 1, 2]
    return Qr


def laminate_matrices(Q, angles_deg, t_ply):
    """
    Matrices homogénéisées A*, B*, D* et C* = A* - D* d'un empilement
    (théorie classique des stratifiés, P2 slide 41) :

        A = somme_k Q_k (z_k - z_{k-1})          A* = A / h
        B = 1/2 somme_k Q_k (z_k^2 - z_{k-1}^2)  B* = 2 B / h^2
        D = 1/3 somme_k Q_k (z_k^3 - z_{k-1}^3)  D* = 12 D / h^3
    """
    angles = np.atleast_1d(angles_deg)
    n = angles.size
    h = n * t_ply

    # Cotes des n+1 interfaces, de -h/2 à +h/2
    z = -h / 2.0 + t_ply * np.arange(n + 1)
    Qk = rotate_stiffness(Q, angles)            # forme (n, 3, 3)

    # Sommes pondérées sur les plis : somme_k w_k Q_k (z[1:] = haut des plis,
    # z[:-1] = bas des plis)
    A = np.tensordot(z[1:] - z[:-1], Qk, axes=1)
    B = np.tensordot((z[1:]**2 - z[:-1]**2) / 2.0, Qk, axes=1)
    D = np.tensordot((z[1:]**3 - z[:-1]**3) / 3.0, Qk, axes=1)

    # Matrices homogénéisées : toutes en MPa, comparables à Q
    A_star = A / h
    B_star = 2.0 * B / h**2
    D_star = 12.0 * D / h**3
    C_star = A_star - D_star
    return A_star, B_star, D_star, C_star
