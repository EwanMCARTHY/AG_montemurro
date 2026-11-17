"""
===============================================================================
STANDARD BINARY-CODED GENETIC ALGORITHM (EVCSP - M. Montemurro)
===============================================================================
Course references: EVCSP_P1 (GA operators, slides 48-53) and EVCSP_P2
(slide 50: genetic data of the laminate example).
Only NumPy is used.

Vocabulary
----------
- individual : one laminate = one candidate solution (20 ply angles)
- gene       : one ply angle, stored on 8 bits
- genotype   : the bits of an individual (20 genes x 8 bits = 160 bits)
- phenotype  : the decoded angles in degrees

Encoding of one angle on 8 bits
-------------------------------
Angles are in ]-90 deg, 90 deg] with a 1 deg step: -89, -88, ..., 0, ..., 90,
i.e. 180 possible values.
- 7 bits give only 2^7 = 128 values: not enough.
- 8 bits give 2^8 = 256 codes (0 to 255): enough, but 256 - 180 = 76 codes
  do not correspond to any angle.

Choice made for the 76 extra codes: REJECTION.
    code 0..179  ->  angle = -89 + code   (0 -> -89 deg, 179 -> +90 deg)
    code 180..255 -> invalid, never kept in the population
- The initial population is drawn among the 180 valid codes only.
- When crossover or mutation creates an invalid code in a child, that gene
  is rejected and the child keeps the gene of its parent at the same place.
Why not modulo (angle = -89 + code % 180)? Codes 0..75 and 180..255 would
then give the same 76 angles, so those angles would be drawn twice as often
as the 104 others: the search would be biased. Rejection keeps every angle
equally likely.
===============================================================================
"""

import numpy as np

import fitness as fit

# Encoding constants of one gene (= one ply)
BITS_PER_GENE = 8      # number of bits per angle
N_VALID_CODES = 180    # codes 0..179 are angles, 180..255 are rejected
ANGLE_MIN = -89        # angle of code 0 [deg]; code 179 gives +90 deg


# =============================================================================
# 1. CONVERSIONS BETWEEN BITS, CODES AND ANGLES
# =============================================================================
def bits_to_codes(pop_bits, n_plies):
    """
    Bits -> integer codes.

    pop_bits : array of 0/1, shape (N, n_plies * 8), one row per individual.
    Returns  : array of integers in [0, 255], shape (N, n_plies).
    """
    pop_size = pop_bits.shape[0]

    # Cut each row of 160 bits into 20 groups of 8 bits: shape (N, 20, 8)
    genes = pop_bits.reshape(pop_size, n_plies, BITS_PER_GENE)

    # Weight of each bit, most significant first: [128, 64, 32, 16, 8, 4, 2, 1]
    weights = 2 ** np.arange(BITS_PER_GENE - 1, -1, -1)

    # Code = sum(bit_j * weight_j). Example: [1,0,0,0,0,0,0,1] -> 128 + 1 = 129
    return genes @ weights


def codes_to_bits(codes):
    """
    Integer codes -> bits (inverse of bits_to_codes).

    codes   : array of integers, shape (N, n_plies).
    Returns : array of 0/1 (int8), shape (N, n_plies * 8).
    """
    # For each code, bit j (from the most significant) is (code >> j) & 1.
    # codes[..., None] adds an axis so that the 8 shifts apply to every code.
    shifts = np.arange(BITS_PER_GENE - 1, -1, -1)
    bits = (codes[..., None] >> shifts) & 1          # shape (N, n_plies, 8)
    return bits.reshape(codes.shape[0], -1).astype(np.int8)


def decode_population(pop_bits, n_plies):
    """
    Genotype (bits) -> phenotype (angles in degrees), shape (N, n_plies).
    Only valid codes (0..179) are ever present in the population.
    """
    return ANGLE_MIN + bits_to_codes(pop_bits, n_plies)


# =============================================================================
# 2. INITIAL POPULATION (P1 slide 48: "N individus obtenus par tirage aleatoire")
# =============================================================================
def init_population(pop_size, n_plies, rng):
    """
    Random generation 0. Each gene is drawn uniformly among the 180 valid
    codes, so every angle has the same probability 1/180.
    Returns the bits, shape (pop_size, n_plies * 8).
    """
    codes = rng.integers(0, N_VALID_CODES, size=(pop_size, n_plies))
    return codes_to_bits(codes)


# =============================================================================
# 3. SELECTION: BIASED ROULETTE WHEEL (P2 slide 50, "roue de loterie biaisee")
# =============================================================================
def roulette_selection(pop_bits, fit_values, rng):
    """
    Draws N parents. Individual i gets a slice of the wheel proportional to
    its fitness f_i: P_i = f_i / sum(f_j). Good individuals are drawn more
    often, weaker ones keep a small chance (except the worst, whose f = 0).
    """
    total = np.sum(fit_values)

    # Safety: if every fitness is zero, all individuals get the same chance
    if total == 0.0:
        probs = np.full(len(fit_values), 1.0 / len(fit_values))
    else:
        probs = fit_values / total

    # N spins of the wheel, with replacement: a very good individual can be
    # chosen several times as a parent.
    indices = rng.choice(len(pop_bits), size=len(pop_bits), replace=True, p=probs)

    # .copy() so that later operators never modify the old population
    return pop_bits[indices].copy()


# =============================================================================
# 4. CROSSOVER: MIXING THE PARENTS' GENOTYPES (P1 slide 48)
# =============================================================================
def crossover_population(parents, p_crossover, rng, crossover_type="one_point"):
    """
    Parents are paired two by two: (0,1), (2,3), (4,5)...
    With probability p_crossover (0.85) the pair exchanges part of its bits
    to make 2 children; otherwise the children are copies of the parents.
    Child i always starts with the bits of parent i (used by the rejection
    step, which falls back on parent i).
    """
    children = parents.copy()
    pop_size, n_bits = parents.shape

    # Step of 2 to build the pairs; "pop_size - 1" handles an odd pop_size
    for i in range(0, pop_size - 1, 2):
        if rng.random() < p_crossover:
            p1 = parents[i]
            p2 = parents[i + 1]

            if crossover_type == "one_point":
                # One cut point "cut" between 1 and 159:
                #   child 1 = [start of P1] + [end of P2]
                #   child 2 = [start of P2] + [end of P1]
                cut = rng.integers(1, n_bits)
                children[i] = np.concatenate([p1[:cut], p2[cut:]])
                children[i + 1] = np.concatenate([p2[:cut], p1[cut:]])

            elif crossover_type == "two_point":
                # Two distinct cut points c1 < c2: only the middle segment
                # [c1:c2] is exchanged between P1 and P2.
                c1, c2 = sorted(rng.choice(np.arange(1, n_bits), size=2, replace=False))
                children[i] = np.concatenate([p1[:c1], p2[c1:c2], p1[c2:]])
                children[i + 1] = np.concatenate([p2[:c1], p1[c1:c2], p2[c2:]])

            else:
                raise ValueError(f"Unknown crossover type: {crossover_type}")

    return children


# =============================================================================
# 5. MUTATION: RANDOM ALTERATION OF THE GENES (P1 slide 53, P2 slide 50)
# =============================================================================
def mutate_population(pop_bits, p_mutation, n_plies, rng):
    """
    Keeps diversity in the population so that the GA does not get stuck.

    As in the course, the probability pm (= 1/N) applies to each GENE:
    each gene of each individual mutates with probability pm, and a
    mutation flips one randomly chosen bit of that gene (0 <-> 1).
    """
    pop_size = pop_bits.shape[0]

    # True where a gene mutates, shape (N, n_plies)
    mask = rng.random((pop_size, n_plies)) < p_mutation

    # Row index and gene index of every mutating gene
    rows, genes = np.nonzero(mask)

    # Position of the flipped bit: first bit of the gene + random offset 0..7
    bit_pos = genes * BITS_PER_GENE + rng.integers(0, BITS_PER_GENE, size=rows.size)

    mutated = pop_bits.copy()
    mutated[rows, bit_pos] = 1 - mutated[rows, bit_pos]   # 1 - 0 = 1, 1 - 1 = 0
    return mutated


# =============================================================================
# 6. REJECTION OF THE INVALID CODES (see the module header)
# =============================================================================
def reject_invalid_genes(children, parents, n_plies):
    """
    Any gene of a child whose code is >= 180 (no angle) is rejected: the
    child takes back the gene of its parent at the same position (parent i
    for child i, always valid). The crossover or mutation is thus cancelled
    for that gene only.

    Returns the repaired children and the number of rejected genes.
    """
    child_codes = bits_to_codes(children, n_plies)
    parent_codes = bits_to_codes(parents, n_plies)

    invalid = child_codes >= N_VALID_CODES
    child_codes[invalid] = parent_codes[invalid]

    return codes_to_bits(child_codes), int(invalid.sum())


# =============================================================================
# 7. EVALUATION OF A POPULATION
# =============================================================================
def evaluate_population(angles, Q, t_ply, objectives, K_A, K_D):
    """
    Cost Phi(delta) of every individual (one row of angles each), computed
    by fitness.cost. The closer to 0, the better the laminate.
    """
    return np.array([
        fit.cost(ind, Q, t_ply, objectives, K_A=K_A, K_D=K_D) for ind in angles
    ])


# =============================================================================
# 8. MAIN LOOP OF THE GA (P1 slide 48: flow chart of the standard GA)
# =============================================================================
def run_ga(
    Q,
    t_ply,
    n_plies,
    objectives,
    pop_size=500,
    n_generations=500,
    p_crossover=0.85,
    p_mutation=0.002,
    selection_pressure=1.0,
    K_A=0,
    K_D=0,
    crossover_type="one_point",
    seed=1,
    verbose=True,
):
    """
    Standard GA with elitism.

    Main inputs (from config.py):
    - Q                  : 3x3 reduced stiffness of the ply [MPa]
    - t_ply              : ply thickness [mm]
    - n_plies            : number of plies (20 for group 1)
    - objectives         : indices of the partial objectives ([1, 4, 9])
    - pop_size           : population size N
    - n_generations      : stopping criterion Ngen
    - p_crossover        : crossover probability pc
    - p_mutation         : mutation probability pm, per gene
    - selection_pressure : exponent p of the fitness (statement: p = 1)
    - crossover_type     : "one_point" or "two_point"
    - seed               : random seed, for reproducible runs

    Returns a dict with the best angles, the best cost and the history
    (one dict of statistics per generation).
    """
    rng = np.random.default_rng(seed)

    # Refuse meaningless combinations of objectives (see fitness.py)
    fit.check_objectives(objectives)

    # --- GENERATION 0: random population and its evaluation ---
    pop_bits = init_population(pop_size, n_plies, rng)
    angles = decode_population(pop_bits, n_plies)
    costs = evaluate_population(angles, Q, t_ply, objectives, K_A, K_D)
    n_rejected = 0          # no rejection for the initial population

    history = []

    for gen in range(n_generations):
        # A. Remember the best individual of the current generation (elitism)
        best_idx = int(np.argmin(costs))
        best_bits = pop_bits[best_idx].copy()
        best_cost = float(costs[best_idx])

        # B. Statistics of the current population (CSV and convergence curve)
        history.append({
            "generation": gen,
            "min": best_cost,
            "mean": float(np.mean(costs)),
            "median": float(np.median(costs)),
            "max": float(np.max(costs)),
            "std": float(np.std(costs)),
            "rejected_genes": n_rejected,
            "best_stacking": "/".join(str(int(a)) for a in angles[best_idx]),
        })

        if verbose and (gen == 0 or (gen + 1) % 50 == 0):
            print(f"Gen {gen + 1:3d}/{n_generations} | best cost = {best_cost:.4e} | "
                  f"mean = {history[-1]['mean']:.4e}")

        # C. Fitness in [0, 1] from the costs (statement 2.a):
        #    best individual -> 1, worst individual -> 0
        fit_vals = fit.fitness(costs, p=selection_pressure)

        # D. Reproduction: selection -> crossover -> mutation -> rejection
        parents = roulette_selection(pop_bits, fit_vals, rng)
        offspring = crossover_population(parents, p_crossover, rng, crossover_type)
        offspring = mutate_population(offspring, p_mutation, n_plies, rng)
        offspring, n_rejected = reject_invalid_genes(offspring, parents, n_plies)

        # E. Evaluation of the children
        offspring_angles = decode_population(offspring, n_plies)
        offspring_costs = evaluate_population(offspring_angles, Q, t_ply, objectives, K_A, K_D)

        # F. Elitism (P1 slide 48): the worst child is replaced by the best
        #    individual of the previous generation, so the best solution found
        #    so far is never lost.
        worst_idx = int(np.argmax(offspring_costs))
        offspring[worst_idx] = best_bits
        offspring_costs[worst_idx] = best_cost

        # G. The children become the current generation
        pop_bits = offspring
        costs = offspring_costs
        angles = decode_population(pop_bits, n_plies)

    # --- END: best individual of the last generation ---
    final_best_idx = int(np.argmin(costs))
    return {
        "best_angles": angles[final_best_idx],
        "best_cost": float(costs[final_best_idx]),
        "history": history,
    }
