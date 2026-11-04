"""
Input data of the problem. Everything the user may want to change lives here.

Units: MPa for moduli, mm for thicknesses, degrees for angles.
"""

# ---------------------------------------------------------------------------
# Ply material (statement, section 1): carbon/epoxy prepreg
# ---------------------------------------------------------------------------
E1 = 161000.0      # longitudinal Young's modulus [MPa]
E2 = 9000.0        # transverse Young's modulus [MPa]
NU12 = 0.26        # major Poisson's ratio [-]
G12 = 6100.0       # in-plane shear modulus [MPa]
T_PLY = 0.125      # ply thickness [mm]

# ---------------------------------------------------------------------------
# Group data (statement, table of section 1)
# Group 1: decoupling, R0-orthotropy in membrane, "R1-orthotropy" in bending
# ---------------------------------------------------------------------------
GROUP = 1
N_PLIES = 20

# Indices of the partial objectives summed in the cost function
# (P2 slides 45-47):
#   1 : decoupling, B* = 0
#   4 : R0-orthotropy of A*, R0(A*) = 0
#   9 : R1(D*) = 0 (called "symetrie du carre" on slide 47)
OBJECTIVES = [1, 4, 9]

# K values used only by the ordinary-orthotropy objectives Phi3 and Phi7
# (P2 slides 46-47, K = 0 or 1). Not used by group 1.
K_A = 0
K_D = 0

# ---------------------------------------------------------------------------
# Genetic algorithm parameters (statement, section 2.a; P2 slide 50)
# ---------------------------------------------------------------------------
POP_SIZE = 500                 # N: number of individuals
N_GENERATIONS = 500            # Ngen: stopping criterion
P_CROSSOVER = 0.85             # pc: crossover probability (P2 slide 50)
P_MUTATION = 1.0 / POP_SIZE    # pm: mutation probability per gene (P2 slide 50)
SELECTION_PRESSURE = 1.0       # p in the fitness formula (statement: p = 1)
SEED = 1                       # random seed, for reproducible runs

# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------
RESULTS_DIR = "results"
