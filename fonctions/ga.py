"""
Algorithme génétique standard à codage binaire (P1 slides 48-53 ; P2 slide 50).

Vocabulaire : un individu = un stratifié (20 angles) ; un gène = un angle,
codé sur 8 bits ; un individu fait donc 20 x 8 = 160 bits.

Codage d'un angle : les angles vont de -89° à +90° au pas de 1°, soit 180
valeurs. 8 bits donnent 256 codes :
    code 0..179   ->  angle = -89 + code
    code 180..255 ->  invalide, REJETÉ : l'enfant garde le gène de son parent
(le modulo ferait tirer 76 angles deux fois plus souvent que les autres).
"""

import numpy as np

import fitness as fit

BITS_PER_GENE = 8      # nombre de bits par angle
N_VALID_CODES = 180    # codes 0..179 valides, 180..255 rejetés
ANGLE_MIN = -89        # angle du code 0 [deg]


# =============================================================================
# 1. CONVERSIONS BITS <-> CODES <-> ANGLES
# =============================================================================
def bits_to_codes(pop_bits, n_plies):
    """Bits (N, n_plies*8) -> codes entiers (N, n_plies)."""
    genes = pop_bits.reshape(pop_bits.shape[0], n_plies, BITS_PER_GENE)
    weights = 2 ** np.arange(BITS_PER_GENE - 1, -1, -1)    # [128, 64, ..., 1]
    return genes @ weights                                 # somme bit x poids


def codes_to_bits(codes):
    """Codes entiers (N, n_plies) -> bits (N, n_plies*8)."""
    shifts = np.arange(BITS_PER_GENE - 1, -1, -1)
    bits = (codes[..., None] >> shifts) & 1                # bit j = (code >> j) & 1
    return bits.reshape(codes.shape[0], -1).astype(np.int8)


def decode_population(pop_bits, n_plies):
    """Bits -> angles en degrés (N, n_plies)."""
    return ANGLE_MIN + bits_to_codes(pop_bits, n_plies)


# =============================================================================
# 2. OPÉRATEURS GÉNÉTIQUES
# =============================================================================
def init_population(pop_size, n_plies, rng):
    """Population initiale : chaque gène est tiré parmi les 180 codes valides."""
    codes = rng.integers(0, N_VALID_CODES, size=(pop_size, n_plies))
    return codes_to_bits(codes)


def roulette_selection(pop_bits, fit_values, rng):
    """
    Roue de loterie biaisée : l'individu i est tiré avec la probabilité
    f_i / somme(f_j). N tirages avec remise.
    """
    probs = fit_values / np.sum(fit_values)
    indices = rng.choice(len(pop_bits), size=len(pop_bits), replace=True, p=probs)
    return pop_bits[indices].copy()


def crossover_population(parents, p_crossover, rng):
    """
    Croisement en un point : les parents sont pris deux par deux ; avec la
    probabilité pc, on coupe au hasard dans les 160 bits et on échange les fins.
    L'enfant i commence toujours par les bits du parent i.
    """
    children = parents.copy()
    pop_size, n_bits = parents.shape
    for i in range(0, pop_size - 1, 2):
        if rng.random() < p_crossover:
            cut = rng.integers(1, n_bits)
            children[i] = np.concatenate([parents[i][:cut], parents[i + 1][cut:]])
            children[i + 1] = np.concatenate([parents[i + 1][:cut], parents[i][cut:]])
    return children


def mutate_population(pop_bits, p_mutation, n_plies, rng):
    """
    Mutation : chaque gène mute avec la probabilité pm ; on inverse alors un
    bit tiré au hasard dans ce gène.
    """
    mask = rng.random((pop_bits.shape[0], n_plies)) < p_mutation
    rows, genes = np.nonzero(mask)                       # gènes qui mutent
    bit_pos = genes * BITS_PER_GENE + rng.integers(0, BITS_PER_GENE, size=rows.size)
    mutated = pop_bits.copy()
    mutated[rows, bit_pos] = 1 - mutated[rows, bit_pos]  # 0 <-> 1
    return mutated


def reject_invalid_genes(children, parents, n_plies):
    """Tout gène d'enfant de code >= 180 reprend le gène du parent au même endroit."""
    child_codes = bits_to_codes(children, n_plies)
    parent_codes = bits_to_codes(parents, n_plies)
    invalid = child_codes >= N_VALID_CODES
    child_codes[invalid] = parent_codes[invalid]
    return codes_to_bits(child_codes)


def evaluate_population(angles, Q, t_ply):
    """Coût de chaque individu (une ligne d'angles par individu)."""
    return np.array([fit.cost(ind, Q, t_ply) for ind in angles])


# =============================================================================
# 3. BOUCLE PRINCIPALE (P1 slide 48)
# =============================================================================
def run_ga(Q, t_ply, n_plies, pop_size, n_generations, p_crossover, p_mutation,
           selection_pressure, seed):
    """
    AG standard avec élitisme. Renvoie les meilleurs angles, le meilleur coût
    et l'historique des statistiques de la population (une entrée par génération).
    """
    rng = np.random.default_rng(seed)

    # Génération 0
    pop_bits = init_population(pop_size, n_plies, rng)
    angles = decode_population(pop_bits, n_plies)
    costs = evaluate_population(angles, Q, t_ply)
    history = []

    for gen in range(n_generations):
        # A. Meilleur individu courant, gardé pour l'élitisme
        best_idx = int(np.argmin(costs))
        best_bits = pop_bits[best_idx].copy()
        best_cost = float(costs[best_idx])

        # B. Statistiques de la population
        history.append({"generation": gen, "min": best_cost, "mean": float(np.mean(costs)),
                        "max": float(np.max(costs)), "std": float(np.std(costs))})
        if gen == 0 or (gen + 1) % 50 == 0:
            print(f"Gen {gen + 1:3d}/{n_generations} | meilleur coût = {best_cost:.4e}")

        # C. Reproduction : fitness -> sélection -> croisement -> mutation -> rejet
        fit_vals = fit.fitness(costs, selection_pressure)
        parents = roulette_selection(pop_bits, fit_vals, rng)
        offspring = crossover_population(parents, p_crossover, rng)
        offspring = mutate_population(offspring, p_mutation, n_plies, rng)
        offspring = reject_invalid_genes(offspring, parents, n_plies)
        offspring_costs = evaluate_population(decode_population(offspring, n_plies), Q, t_ply)

        # D. Élitisme : le pire enfant est remplacé par le meilleur de la génération précédente
        worst_idx = int(np.argmax(offspring_costs))
        offspring[worst_idx] = best_bits
        offspring_costs[worst_idx] = best_cost

        # E. Les enfants deviennent la génération courante
        pop_bits = offspring
        costs = offspring_costs
        angles = decode_population(pop_bits, n_plies)

    best_idx = int(np.argmin(costs))
    return angles[best_idx], float(costs[best_idx]), history
