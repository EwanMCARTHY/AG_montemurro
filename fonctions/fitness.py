"""
Fonction de coût (somme des objectifs partiels) et fitness de l'AG.

Objectifs partiels : P2 slides 45-47. Ils sont tous sans dimension et valent
zéro quand la symétrie élastique visée est atteinte : le minimum théorique
de la fonction de coût est donc 0 (P2 slide 44).

Fitness : énoncé, section 2.a.
"""

import numpy as np

import laminate as lam
import polar as pol

# Paires d'objectifs qu'on n'a pas le droit de combiner.
# Phi3, Phi7 et Phi11 utilisent des angles polaires ; or un angle polaire n'est
# pas défini quand le module R correspondant est nul (P2 slide 38). On ne peut
# donc pas, sur le même tenseur, viser un angle ET annuler R0 ou R1 :
#   Phi3 (angles de A*) avec Phi4, Phi5, Phi6 (qui annulent R0 ou R1 de A*)
#   Phi7 (angles de D*) avec Phi8, Phi9, Phi10 (qui annulent R0 ou R1 de D*)
#   Phi11 (Phi1 de A* et de D*) avec Phi5, Phi6, Phi9, Phi10 (qui annulent R1)
FORBIDDEN_PAIRS = [
    (3, 4), (3, 5), (3, 6),
    (7, 8), (7, 9), (7, 10),
    (11, 5), (11, 6), (11, 9), (11, 10),
]


def check_objectives(objectives):
    """
    Lève une erreur si la liste d'objectifs contient un numéro inconnu ou
    une paire interdite (voir FORBIDDEN_PAIRS).
    """
    for obj in objectives:
        if obj not in range(1, 12):
            raise ValueError(f"Objectif partiel inconnu : Phi{obj}")
    for a, b in FORBIDDEN_PAIRS:
        if a in objectives and b in objectives:
            raise ValueError(f"Phi{a} et Phi{b} ne peuvent pas être combinés : "
                             "un angle polaire n'est pas défini quand R = 0")


def wrap_angle(x, period):
    """
    Ramène un angle dans [-period/2, period/2[.

    Phi0 est défini à pi/2 près et Phi1 à pi près, donc Phi0 - Phi1 n'est
    défini qu'à pi/2 près : l'écart à K pi/4 doit être mesuré « sur ce
    cercle », sinon un stratifié pile sur la cible peut paraître loin d'elle.
    """
    return (x + period / 2.0) % period - period / 2.0


def partial_objectives(ppA, ppB, ppD, ppC, pp_ply, K_A=0, K_D=0):
    """
    Les onze objectifs partiels des slides 45-47 de P2, dans un dictionnaire
    {numéro: valeur}.

    ppA, ppB, ppD, ppC : paramètres polaires de A*, B*, D*, C = A* - D*
    pp_ply             : paramètres polaires de la rigidité Q du pli
    K_A, K_D           : K = 0 ou 1 pour les objectifs d'orthotropie ordinaire
    """
    norm_Q = pol.polar_norm(pp_ply)
    R0, R1 = pp_ply["R0"], pp_ply["R1"]
    quarter_pi = np.pi / 4.0

    phi = {}
    # --- Slide 45 ---
    phi[1] = (pol.polar_norm(ppB) / norm_Q)**2            # découplage B* = 0
    phi[2] = (pol.polar_norm(ppC) / norm_Q)**2            # homogénéité C = 0

    # --- Slide 46 : membrane (A*) ---
    dA = wrap_angle(ppA["Phi0"] - ppA["Phi1"] - K_A * quarter_pi, np.pi / 2.0)
    phi[3] = (dA / quarter_pi)**2                          # orthotropie ordinaire
    phi[4] = (ppA["R0"] / R0)**2                           # orthotropie R0
    phi[5] = (ppA["R1"] / R1)**2                           # symétrie du carré
    phi[6] = (ppA["R0"]**2 + 4 * ppA["R1"]**2) / (R0**2 + 4 * R1**2)  # isotropie

    # --- Slide 47 : flexion (D*) ---
    dD = wrap_angle(ppD["Phi0"] - ppD["Phi1"] - K_D * quarter_pi, np.pi / 2.0)
    phi[7] = (dD / quarter_pi)**2                          # orthotropie ordinaire
    phi[8] = (ppD["R0"] / R0)**2                           # orthotropie R0
    phi[9] = (ppD["R1"] / R1)**2                           # symétrie du carré
    phi[10] = (ppD["R0"]**2 + 4 * ppD["R1"]**2) / (R0**2 + 4 * R1**2)  # isotropie

    # --- Slide 47 : axes d'orthotropie de membrane et de flexion confondus ---
    d1 = wrap_angle(ppA["Phi1"] - ppD["Phi1"], np.pi)     # Phi1 défini à pi près
    phi[11] = (d1 / quarter_pi)**2
    return phi


def laminate_polar(Q, angles_deg, t_ply):
    """Paramètres polaires de A*, B*, D*, C d'un empilement (voie cartésienne)."""
    A_s, B_s, D_s, C = lam.laminate_matrices(Q, angles_deg, t_ply)
    return (pol.polar_parameters(A_s), pol.polar_parameters(B_s),
            pol.polar_parameters(D_s), pol.polar_parameters(C))


def cost(angles_deg, Q, t_ply, objectives, K_A=0, K_D=0):
    """
    Fonction de coût Phi(delta) = somme des objectifs partiels choisis
    (P2 slide 44). Son minimum théorique est 0.
    """
    pp_ply = pol.polar_parameters(Q)
    ppA, ppB, ppD, ppC = laminate_polar(Q, angles_deg, t_ply)
    phi = partial_objectives(ppA, ppB, ppD, ppC, pp_ply, K_A, K_D)
    return sum(phi[i] for i in objectives)


def fitness(costs, p=1.0):
    """
    Fitness des N individus (énoncé, section 2.a) :

        f_i = (1 - (Phi_i - min Phi) / (max Phi - min Phi))^p

    Le meilleur individu (coût le plus bas) a f = 1, le pire f = 0.
    Si tous les coûts sont égaux, tout le monde a f = 1 (aucune préférence).
    """
    costs = np.asarray(costs, dtype=float)
    c_min, c_max = costs.min(), costs.max()
    if c_max == c_min:
        return np.ones_like(costs)
    return (1.0 - (costs - c_min) / (c_max - c_min))**p
