"""
Méthode polaire de G. Verchery (1979) pour les tenseurs d'élasticité plane
d'ordre 4 (P2 slides 35-42).

Un tenseur L (n'importe laquelle de nos matrices : Q, A*, B*, D* ou C) est
décrit par :
    T0, T1     : modules isotropes
    R0, R1     : modules anisotropes
    Phi0, Phi1 : angles polaires
Seuls T0, T1, R0, R1 et la différence Phi0 - Phi1 sont des invariants
(ils ne changent pas quand on tourne le repère).

Les paramètres polaires sont rangés dans un dictionnaire avec les clés
"T0", "T1", "R0", "R1", "Phi0", "Phi1" (angles en radians).
"""

import numpy as np


def _from_complex(T0, T1, z0, z1):
    """
    Construit le dictionnaire des paramètres polaires à partir de T0, T1 et
    des deux nombres complexes z0 = R0 e^(4i Phi0) et z1 = R1 e^(2i Phi1) :
    le module donne R, l'argument donne l'angle.
    """
    return {
        "T0": T0,
        "T1": T1,
        "R0": np.abs(z0),
        "R1": np.abs(z1),
        "Phi0": np.angle(z0) / 4.0,   # Phi0 dans ]-pi/4, pi/4]
        "Phi1": np.angle(z1) / 2.0,   # Phi1 dans ]-pi/2, pi/2]
    }


def polar_parameters(L):
    """
    Paramètres polaires d'une matrice 3x3 de type rigidité L (loi inverse,
    P2 slide 36). Composantes de Voigt :
        L1111 = L11, L1122 = L12, L1212 = L66,
        L1112 = L16, L2212 = L26, L2222 = L22

        8 T0             = L11 - 2 L12 + 4 L66 + L22
        8 T1             = L11 + 2 L12 + L22
        8 R0 e^(4i Phi0) = L11 + 4i L16 - 2 L12 - 4 L66 - 4i L26 + L22
        8 R1 e^(2i Phi1) = L11 + 2i L16 + 2i L26 - L22

    Phi0 et Phi1 n'ont pas de sens (bruit numérique) quand R0 ou R1 est nul.
    """
    L11, L12, L16 = L[0, 0], L[0, 1], L[0, 2]
    L22, L26, L66 = L[1, 1], L[1, 2], L[2, 2]

    T0 = (L11 - 2 * L12 + 4 * L66 + L22) / 8.0
    T1 = (L11 + 2 * L12 + L22) / 8.0
    # En Python, 1j est le nombre imaginaire i
    z0 = (L11 + 4j * L16 - 2 * L12 - 4 * L66 - 4j * L26 + L22) / 8.0
    z1 = (L11 + 2j * L16 + 2j * L26 - L22) / 8.0

    return _from_complex(T0, T1, z0, z1)


def stiffness_from_polar(pp, theta=0.0):
    """
    Composantes cartésiennes d'un tenseur à partir de ses paramètres polaires
    (P2 slide 35), dans un repère tourné de theta [rad]. Tourner le repère
    revient simplement à retrancher theta aux angles polaires (P2 slide 37).

    Renvoie la matrice de Voigt 3x3.
    """
    T0, T1, R0, R1 = pp["T0"], pp["T1"], pp["R0"], pp["R1"]
    a0 = 4.0 * (pp["Phi0"] - theta)
    a1 = 2.0 * (pp["Phi1"] - theta)

    L11 = T0 + 2 * T1 + R0 * np.cos(a0) + 4 * R1 * np.cos(a1)
    L16 = R0 * np.sin(a0) + 2 * R1 * np.sin(a1)
    L12 = -T0 + 2 * T1 - R0 * np.cos(a0)
    L66 = T0 - R0 * np.cos(a0)
    L26 = -R0 * np.sin(a0) + 2 * R1 * np.sin(a1)
    L22 = T0 + 2 * T1 + R0 * np.cos(a0) - 4 * R1 * np.cos(a1)

    return np.array([
        [L11, L12, L16],
        [L12, L22, L26],
        [L16, L26, L66],
    ])


def polar_norm(pp):
    """
    Norme d'un tenseur d'élasticité plane d'ordre 4 (P2 slide 45) :
        ||L|| = sqrt(T0^2 + 2 T1^2 + R0^2 + 4 R1^2)
    """
    return np.sqrt(pp["T0"]**2 + 2 * pp["T1"]**2 + pp["R0"]**2 + 4 * pp["R1"]**2)


def laminate_polar_direct(ply_pp, angles_deg):
    """
    Paramètres polaires de A*, B*, D* et C calculés directement à partir de
    ceux du pli, sans aucune matrice cartésienne (P2 slides 41-42) :

        A* : T0, T1 du pli,
             R0 e^(4i Phi0) = (1/n)   R0 e^(4i Phi0_pli) somme_k       e^(4i delta_k)
             R1 e^(2i Phi1) = (1/n)   R1 e^(2i Phi1_pli) somme_k       e^(2i delta_k)
        B* : T0 = T1 = 0,
             pareil avec (1/n^2) somme_k b_k e^(...)
        D* : T0, T1 du pli,
             pareil avec (1/n^3) somme_k d_k e^(...)
        C = A* - D* : T0 = T1 = 0, différence des nombres complexes

    Les coefficients b_k et d_k viennent de B* = 2B/h^2 et D* = 12D/h^3,
    avec h = n t et les interfaces z_k de laminate.ply_interfaces :
        b_k = (z_k^2 - z_{k-1}^2) / t^2
        d_k = 4 (z_k^3 - z_{k-1}^3) / t^3
    En entiers (z_k / t = k - n/2) : b_k = 2k - n - 1,
    d_k = 12 k (k - n - 1) + 4 + 3 n (n + 2).

    Sert de vérification indépendante de la voie cartésienne (tests).
    """
    delta = np.radians(np.atleast_1d(angles_deg).astype(float))
    n = delta.size

    # Cotes des interfaces sans dimension z_k / t, k = 0..n
    zt = -n / 2.0 + np.arange(n + 1)
    b = zt[1:]**2 - zt[:-1]**2
    d = 4.0 * (zt[1:]**3 - zt[:-1]**3)

    # Les « flèches » de chaque pli : e^(4i delta_k) et e^(2i delta_k)
    e4 = np.exp(4j * delta)
    e2 = np.exp(2j * delta)

    # Modules polaires complexes du pli : R0 e^(4i Phi0), R1 e^(2i Phi1)
    z0_ply = ply_pp["R0"] * np.exp(4j * ply_pp["Phi0"])
    z1_ply = ply_pp["R1"] * np.exp(2j * ply_pp["Phi1"])

    # Sommes des flèches, pondérées par b_k (couplage) ou d_k (flexion)
    zA0 = z0_ply * np.sum(e4) / n
    zA1 = z1_ply * np.sum(e2) / n
    zB0 = z0_ply * np.sum(b * e4) / n**2
    zB1 = z1_ply * np.sum(b * e2) / n**2
    zD0 = z0_ply * np.sum(d * e4) / n**3
    zD1 = z1_ply * np.sum(d * e2) / n**3

    T0, T1 = ply_pp["T0"], ply_pp["T1"]
    return {
        "A": _from_complex(T0, T1, zA0, zA1),
        "B": _from_complex(0.0, 0.0, zB0, zB1),
        "D": _from_complex(T0, T1, zD0, zD1),
        "C": _from_complex(0.0, 0.0, zA0 - zD0, zA1 - zD1),
    }
