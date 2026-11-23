"""
Matrices de rigidité du pli et du stratifié, par la voie cartésienne
(énoncé, section 2.b).

Conventions
-----------
- Notation de Voigt dans le plan, avec la distorsion d'angle gamma_12 :
  {sigma_11, sigma_22, sigma_12} = Q {eps_11, eps_22, gamma_12}.
  Les indices 1, 2, 6 correspondent à 11, 22 et 12 : Q[2, 2] = Q66 (= Q1212
  en notation tensorielle) et Q[0, 2] = Q16 (= Q1112).
- Le pli k occupe z_{k-1} <= z <= z_k, avec z_0 = -h/2 (face du bas) et
  z_n = +h/2 (face du haut). Le pli 1 est le premier angle de la liste.
- Les angles sont en degrés ; un pli d'angle delta a ses fibres tournées de
  +delta (sens trigonométrique) par rapport à l'axe x de la plaque.
"""

import numpy as np


def ply_compliance(E1, E2, nu12, G12):
    """
    Matrice de souplesse réduite S d'un pli orthotrope, dans ses axes
    (énoncé 2.b, « calcul de la matrice de souplesse S du pli »).

    eps = S sigma, avec
        S11 = 1/E1, S12 = -nu12/E1, S22 = 1/E2, S66 = 1/G12.
    """
    S = np.array([
        [1.0 / E1,   -nu12 / E1, 0.0],
        [-nu12 / E1,  1.0 / E2,  0.0],
        [0.0,         0.0,       1.0 / G12],
    ])
    return S


def ply_stiffness(S):
    """
    Matrice de rigidité réduite Q du pli : Q = S^-1 (énoncé 2.b).
    """
    return np.linalg.inv(S)


def rotate_stiffness(Q, angles_deg):
    """
    Matrices de rigidité de plis tournés des angles delta (changement de
    repère cartésien d'un tenseur d'ordre 4, P2 slide 27).

    Q          : rigidité 3x3 du pli dans ses axes (orthotrope : Q16 = Q26 = 0).
    angles_deg : un angle ou un tableau de n angles [deg].

    Renvoie un tableau de forme (n, 3, 3) : une matrice tournée par pli.
    On utilise les formules explicites classiques (c = cos delta, s = sin delta).
    """
    delta = np.radians(np.atleast_1d(angles_deg).astype(float))
    c = np.cos(delta)
    s = np.sin(delta)
    Q11, Q12, Q22, Q66 = Q[0, 0], Q[0, 1], Q[1, 1], Q[2, 2]

    # Chaque ligne calcule une case de la matrice, pour tous les plis à la fois
    Qr = np.zeros((delta.size, 3, 3))
    Qr[:, 0, 0] = Q11 * c**4 + 2 * (Q12 + 2 * Q66) * s**2 * c**2 + Q22 * s**4
    Qr[:, 1, 1] = Q11 * s**4 + 2 * (Q12 + 2 * Q66) * s**2 * c**2 + Q22 * c**4
    Qr[:, 0, 1] = (Q11 + Q22 - 4 * Q66) * s**2 * c**2 + Q12 * (s**4 + c**4)
    Qr[:, 2, 2] = (Q11 + Q22 - 2 * Q12 - 2 * Q66) * s**2 * c**2 + Q66 * (s**4 + c**4)
    Qr[:, 0, 2] = (Q11 - Q12 - 2 * Q66) * s * c**3 + (Q12 - Q22 + 2 * Q66) * s**3 * c
    Qr[:, 1, 2] = (Q11 - Q12 - 2 * Q66) * s**3 * c + (Q12 - Q22 + 2 * Q66) * s * c**3

    # Les matrices sont symétriques : on recopie le triangle du haut en bas
    Qr[:, 1, 0] = Qr[:, 0, 1]
    Qr[:, 2, 0] = Qr[:, 0, 2]
    Qr[:, 2, 1] = Qr[:, 1, 2]
    return Qr


def ply_interfaces(n_plies, t_ply):
    """
    Cotes z des n+1 interfaces entre plis, de z_0 = -h/2 à z_n = +h/2.
    """
    h = n_plies * t_ply
    return -h / 2.0 + t_ply * np.arange(n_plies + 1)


def abd_matrices(Q, angles_deg, t_ply):
    """
    Matrices de membrane A, de couplage B et de flexion D d'un stratifié à
    plis identiques (théorie classique des stratifiés, P2 slide 41) :

        A = somme_k Q_k (z_k - z_{k-1})
        B = 1/2 somme_k Q_k (z_k^2 - z_{k-1}^2)
        D = 1/3 somme_k Q_k (z_k^3 - z_{k-1}^3)
    """
    angles = np.atleast_1d(angles_deg)
    z = ply_interfaces(angles.size, t_ply)
    Qk = rotate_stiffness(Q, angles)            # forme (n, 3, 3)

    # Poids de chaque pli, forme (n,) : z[1:] contient z_1..z_n et
    # z[:-1] contient z_0..z_{n-1}
    w_A = z[1:] - z[:-1]
    w_B = (z[1:]**2 - z[:-1]**2) / 2.0
    w_D = (z[1:]**3 - z[:-1]**3) / 3.0

    # Sommes pondérées sur les plis : somme_k w_k * Q_k.
    # np.tensordot(w, Qk, axes=1) fait exactement cette somme.
    A = np.tensordot(w_A, Qk, axes=1)
    B = np.tensordot(w_B, Qk, axes=1)
    D = np.tensordot(w_D, Qk, axes=1)
    return A, B, D


def homogenised_matrices(A, B, D, h):
    """
    Matrices homogénéisées (normalisées) (P2 slide 41, énoncé 2.b) :

        A* = A / h,   B* = 2 B / h^2,   D* = 12 D / h^3,   C = A* - D*

    A*, B* et D* ont toutes la dimension d'un module [MPa] : on peut les
    comparer directement à Q.
    """
    A_star = A / h
    B_star = 2.0 * B / h**2
    D_star = 12.0 * D / h**3
    C = A_star - D_star
    return A_star, B_star, D_star, C


def laminate_matrices(Q, angles_deg, t_ply):
    """
    Raccourci : matrices homogénéisées A*, B*, D*, C d'une séquence
    d'empilement, par la voie cartésienne.
    """
    angles = np.atleast_1d(angles_deg)
    A, B, D = abd_matrices(Q, angles, t_ply)
    h = angles.size * t_ply
    return homogenised_matrices(A, B, D, h)
