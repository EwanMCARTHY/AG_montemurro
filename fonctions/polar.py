"""
Méthode polaire de G. Verchery (P2 slides 35-38 et 45).

Une matrice de rigidité L (Q, A*, B*, D* ou C*) est décrite par :
    T0, T1     : modules isotropes
    R0, R1     : modules anisotropes
    Phi0, Phi1 : angles polaires (en radians)
rangés dans un dictionnaire {"T0", "T1", "R0", "R1", "Phi0", "Phi1"}.
"""

import numpy as np


def polar_parameters(L):
    """
    Paramètres polaires d'une matrice 3x3 L (P2 slide 36) :
        8 T0             = L11 - 2 L12 + 4 L66 + L22
        8 T1             = L11 + 2 L12 + L22
        8 R0 e^(4i Phi0) = L11 + 4i L16 - 2 L12 - 4 L66 - 4i L26 + L22
        8 R1 e^(2i Phi1) = L11 + 2i L16 + 2i L26 - L22
    Phi0 et Phi1 n'ont pas de sens quand R0 ou R1 est nul.
    """
    L11, L12, L16 = L[0, 0], L[0, 1], L[0, 2]
    L22, L26, L66 = L[1, 1], L[1, 2], L[2, 2]

    # R et Phi sont regroupés dans un nombre complexe (1j est le i de Python) :
    # le module donne R, l'argument donne l'angle
    z0 = (L11 + 4j * L16 - 2 * L12 - 4 * L66 - 4j * L26 + L22) / 8.0
    z1 = (L11 + 2j * L16 + 2j * L26 - L22) / 8.0

    return {
        "T0": (L11 - 2 * L12 + 4 * L66 + L22) / 8.0,
        "T1": (L11 + 2 * L12 + L22) / 8.0,
        "R0": np.abs(z0),
        "R1": np.abs(z1),
        "Phi0": np.angle(z0) / 4.0,
        "Phi1": np.angle(z1) / 2.0,
    }


def polar_norm(pp):
    """Norme d'un tenseur (P2 slide 45) : sqrt(T0^2 + 2 T1^2 + R0^2 + 4 R1^2)."""
    return np.sqrt(pp["T0"]**2 + 2 * pp["T1"]**2 + pp["R0"]**2 + 4 * pp["R1"]**2)


def component_11(pp, theta):
    """
    Composante L11(theta) dans un repère tourné de theta [rad] (P2 slides 35
    et 37) : tourner le repère revient à retrancher theta aux angles polaires.
    Sert aux diagrammes polaires.
    """
    return (pp["T0"] + 2 * pp["T1"]
            + pp["R0"] * np.cos(4 * (pp["Phi0"] - theta))
            + 4 * pp["R1"] * np.cos(2 * (pp["Phi1"] - theta)))
