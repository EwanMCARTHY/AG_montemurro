"""
Ply and laminate stiffness matrices, Cartesian route (statement, section 2.b).

Conventions
-----------
- In-plane Voigt notation with engineering shear strain:
  {sigma_11, sigma_22, sigma_12} = Q {eps_11, eps_22, gamma_12}.
  So Q[2, 2] = Q66 = Q1212 and Q[0, 2] = Q16 = Q1112 in tensor notation.
- Ply k occupies z_{k-1} <= z <= z_k, with z_0 = -h/2 (bottom face) and
  z_n = +h/2 (top face). Ply 1 is the first angle of the stacking list.
- Angles are given in degrees; a ply at angle delta has its fibres rotated
  by +delta (counter-clockwise) from the laminate x axis.
"""

import numpy as np


def ply_compliance(E1, E2, nu12, G12):
    """
    Reduced compliance matrix S of an orthotropic ply in its material axes
    (statement 2.b, "calcul de la matrice de souplesse S du pli").

    eps = S sigma, with
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
    Reduced stiffness matrix Q of the ply: Q = S^-1 (statement 2.b).
    """
    return np.linalg.inv(S)


def rotate_stiffness(Q, angles_deg):
    """
    Stiffness matrix of plies rotated by the angles delta (Cartesian
    transformation of a 4th-order tensor, P2 slide 27).

    Q          : 3x3 stiffness of the ply in its material axes
                 (orthotropic: Q16 = Q26 = 0).
    angles_deg : one angle or an array of n angles [deg].

    Returns an array of shape (n, 3, 3): one rotated matrix per ply.
    The classical explicit formulas are used (c = cos delta, s = sin delta).
    """
    delta = np.radians(np.atleast_1d(angles_deg).astype(float))
    c = np.cos(delta)
    s = np.sin(delta)
    Q11, Q12, Q22, Q66 = Q[0, 0], Q[0, 1], Q[1, 1], Q[2, 2]

    Qr = np.zeros((delta.size, 3, 3))
    Qr[:, 0, 0] = Q11 * c**4 + 2 * (Q12 + 2 * Q66) * s**2 * c**2 + Q22 * s**4
    Qr[:, 1, 1] = Q11 * s**4 + 2 * (Q12 + 2 * Q66) * s**2 * c**2 + Q22 * c**4
    Qr[:, 0, 1] = (Q11 + Q22 - 4 * Q66) * s**2 * c**2 + Q12 * (s**4 + c**4)
    Qr[:, 2, 2] = (Q11 + Q22 - 2 * Q12 - 2 * Q66) * s**2 * c**2 + Q66 * (s**4 + c**4)
    Qr[:, 0, 2] = (Q11 - Q12 - 2 * Q66) * s * c**3 + (Q12 - Q22 + 2 * Q66) * s**3 * c
    Qr[:, 1, 2] = (Q11 - Q12 - 2 * Q66) * s**3 * c + (Q12 - Q22 + 2 * Q66) * s * c**3

    # The matrices are symmetric: copy the upper triangle into the lower one
    Qr[:, 1, 0] = Qr[:, 0, 1]
    Qr[:, 2, 0] = Qr[:, 0, 2]
    Qr[:, 2, 1] = Qr[:, 1, 2]
    return Qr


def ply_interfaces(n_plies, t_ply):
    """
    z coordinates of the n+1 ply interfaces, from z_0 = -h/2 to z_n = +h/2.
    """
    h = n_plies * t_ply
    return -h / 2.0 + t_ply * np.arange(n_plies + 1)


def abd_matrices(Q, angles_deg, t_ply):
    """
    Membrane A, coupling B and bending D matrices of a laminate made of
    identical plies (Classical Laminate Theory, P2 slide 41):

        A = sum_k Q_k (z_k - z_{k-1})
        B = 1/2 sum_k Q_k (z_k^2 - z_{k-1}^2)
        D = 1/3 sum_k Q_k (z_k^3 - z_{k-1}^3)
    """
    angles = np.atleast_1d(angles_deg)
    z = ply_interfaces(angles.size, t_ply)
    Qk = rotate_stiffness(Q, angles)            # shape (n, 3, 3)

    # Weights of each ply, shape (n,)
    w_A = z[1:] - z[:-1]
    w_B = (z[1:]**2 - z[:-1]**2) / 2.0
    w_D = (z[1:]**3 - z[:-1]**3) / 3.0

    # Weighted sums over the plies: sum_k w_k * Q_k
    A = np.tensordot(w_A, Qk, axes=1)
    B = np.tensordot(w_B, Qk, axes=1)
    D = np.tensordot(w_D, Qk, axes=1)
    return A, B, D


def homogenised_matrices(A, B, D, h):
    """
    Homogenised (normalised) matrices (P2 slide 41, statement 2.b):

        A* = A / h,   B* = 2 B / h^2,   D* = 12 D / h^3,   C = A* - D*

    A*, B* and D* all have the dimension of a modulus [MPa], so they can be
    compared directly with Q.
    """
    A_star = A / h
    B_star = 2.0 * B / h**2
    D_star = 12.0 * D / h**3
    C = A_star - D_star
    return A_star, B_star, D_star, C


def laminate_matrices(Q, angles_deg, t_ply):
    """
    Convenience function: homogenised matrices A*, B*, D*, C of a stacking
    sequence, through the Cartesian route.
    """
    angles = np.atleast_1d(angles_deg)
    A, B, D = abd_matrices(Q, angles, t_ply)
    h = angles.size * t_ply
    return homogenised_matrices(A, B, D, h)
