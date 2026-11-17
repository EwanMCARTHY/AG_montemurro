"""
Données d'entrée du problème. Tout ce qu'on peut vouloir modifier est ici.

Unités : MPa pour les modules, mm pour les épaisseurs, degrés pour les angles.
"""

# ---------------------------------------------------------------------------
# Matériau du pli (énoncé, section 1) : pré-imprégné carbone/époxyde
# ---------------------------------------------------------------------------
E1 = 161000.0      # module d'Young longitudinal, sens des fibres [MPa]
E2 = 9000.0        # module d'Young transverse, perpendiculaire aux fibres [MPa]
NU12 = 0.26        # coefficient de Poisson [-]
G12 = 6100.0       # module de cisaillement dans le plan [MPa]
T_PLY = 0.125      # épaisseur d'un pli [mm]

# ---------------------------------------------------------------------------
# Données du groupe (énoncé, tableau de la section 1)
# Groupe 1 : découplage, orthotropie R0 en membrane, « orthotropie R1 » en flexion
# ---------------------------------------------------------------------------
GROUP = 1
N_PLIES = 20

# Numéros des objectifs partiels additionnés dans la fonction de coût
# (P2 slides 45-47) :
#   1 : découplage, B* = 0
#   4 : orthotropie R0 de la membrane, R0(A*) = 0
#   9 : R1(D*) = 0 (appelé « symétrie du carré » sur la slide 47)
# Si le prof confirme que « orthotropie R1 » est une coquille pour
# « orthotropie R0 » en flexion, remplacer 9 par 8 : R0(D*) = 0.
OBJECTIVES = [1, 4, 9]

# Valeurs de K utilisées seulement par les objectifs d'orthotropie ordinaire
# Phi3 et Phi7 (P2 slides 46-47, K = 0 ou 1). Pas utilisées par le groupe 1.
K_A = 0
K_D = 0

# ---------------------------------------------------------------------------
# Paramètres de l'algorithme génétique (énoncé, section 2.a ; P2 slide 50)
# ---------------------------------------------------------------------------
POP_SIZE = 500                 # N : nombre d'individus
N_GENERATIONS = 500            # Ngen : critère d'arrêt
P_CROSSOVER = 0.85             # pc : probabilité de croisement (P2 slide 50)
P_MUTATION = 1.0 / POP_SIZE    # pm : probabilité de mutation par gène (P2 slide 50)
SELECTION_PRESSURE = 1.0       # p dans la formule de la fitness (énoncé : p = 1)
SEED = 1                       # graine du hasard, pour des calculs reproductibles

# ---------------------------------------------------------------------------
# Sorties
# ---------------------------------------------------------------------------
RESULTS_DIR = "results"        # dossier des résultats, à côté de main.py
