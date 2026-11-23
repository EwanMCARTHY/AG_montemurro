"""
Fonction de coût du groupe 1 et fitness de l'AG.

Objectifs partiels (P2 slides 45-47), sans dimension, nuls quand la symétrie
visée est atteinte (le minimum théorique du coût est donc 0) :
    Phi1 = (||B*|| / ||Q||)^2   découplage membrane/flexion (B* = 0)
    Phi4 = (R0(A*) / R0)^2      orthotropie R0 en membrane
    Phi9 = (R1(D*) / R1)^2      symétrie du carré en flexion
(R0 et R1 sans indice sont ceux du pli.)
"""

import numpy as np

import laminate as lam
import polar as pol


def cost(angles_deg, Q, t_ply):
    """Coût d'un empilement : Phi = Phi1 + Phi4 + Phi9 (P2 slide 44)."""
    pp_ply = pol.polar_parameters(Q)
    A_star, B_star, D_star, _ = lam.laminate_matrices(Q, angles_deg, t_ply)
    ppA = pol.polar_parameters(A_star)
    ppB = pol.polar_parameters(B_star)
    ppD = pol.polar_parameters(D_star)

    phi1 = (pol.polar_norm(ppB) / pol.polar_norm(pp_ply))**2
    phi4 = (ppA["R0"] / pp_ply["R0"])**2
    phi9 = (ppD["R1"] / pp_ply["R1"])**2
    return phi1 + phi4 + phi9


def fitness(costs, p):
    """
    Fitness des N individus (énoncé 2.a) :
        f_i = (1 - (Phi_i - min Phi) / (max Phi - min Phi))^p
    Meilleur individu : f = 1 ; pire : f = 0.
    """
    c_min, c_max = costs.min(), costs.max()
    if c_max == c_min:                 # tous égaux : aucune préférence
        return np.ones_like(costs)
    return (1.0 - (costs - c_min) / (c_max - c_min))**p
