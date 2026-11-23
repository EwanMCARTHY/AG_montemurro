"""
Données d'entrée du problème (énoncé, sections 1 et 2.a).
Unités : MPa pour les modules, mm pour les épaisseurs, degrés pour les angles.
"""

# Matériau du pli : pré-imprégné carbone/époxyde
E1 = 161000.0      # module d'Young dans le sens des fibres [MPa]
E2 = 9000.0        # module d'Young perpendiculaire aux fibres [MPa]
NU12 = 0.26        # coefficient de Poisson [-]
G12 = 6100.0       # module de cisaillement dans le plan [MPa]
T_PLY = 0.125      # épaisseur d'un pli [mm]

# Groupe 1 : 20 plis ; découplage, orthotropie R0 en membrane, symétrie du
# carré (R1 = 0) en flexion (l'« orthotropie R1 » de l'énoncé est une
# coquille, confirmée par M. Montemurro)
N_PLIES = 20

# Paramètres de l'algorithme génétique (énoncé 2.a ; P2 slide 50)
POP_SIZE = 500                 # N : nombre d'individus
N_GENERATIONS = 500            # Ngen : nombre de générations
P_CROSSOVER = 0.85             # pc : probabilité de croisement
P_MUTATION = 1.0 / POP_SIZE    # pm : probabilité de mutation d'un gène
SELECTION_PRESSURE = 1.0       # p : pression de sélection de la fitness (énoncé : p = 1)
SEED = 1                       # graine du hasard, pour des calculs reproductibles
