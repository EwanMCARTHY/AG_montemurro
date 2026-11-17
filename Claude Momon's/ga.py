"""
===============================================================================
ALGORITHME GÉNÉTIQUE STANDARD À CODAGE BINAIRE (EVCSP - M. Montemurro)
===============================================================================
Références du cours : EVCSP_P1 (opérateurs de l'AG, slides 48-53) et
EVCSP_P2 (slide 50 : données génétiques de l'exemple de stratifié).
Seul NumPy est utilisé.

Vocabulaire
-----------
- individu  : un stratifié = une solution candidate (20 angles de plis)
- gène      : un angle de pli, stocké sur 8 bits
- génotype  : les bits d'un individu (20 gènes x 8 bits = 160 bits)
- phénotype : les angles décodés, en degrés

Codage d'un angle sur 8 bits
----------------------------
Les angles sont dans ]-90°, 90°] au pas de 1° : -89, -88, ..., 0, ..., 90,
soit 180 valeurs possibles.
- 7 bits ne donnent que 2^7 = 128 valeurs : pas assez.
- 8 bits donnent 2^8 = 256 codes (de 0 à 255) : assez, mais 256 - 180 = 76
  codes ne correspondent à aucun angle.

Choix fait pour les 76 codes en trop : le REJET.
    code 0..179   ->  angle = -89 + code   (0 -> -89°, 179 -> +90°)
    code 180..255 ->  invalide, jamais gardé dans la population
- La population initiale est tirée parmi les 180 codes valides uniquement.
- Quand un croisement ou une mutation crée un code invalide chez un enfant,
  ce gène est rejeté : l'enfant garde le gène de son parent au même endroit.
Pourquoi pas le modulo (angle = -89 + code % 180) ? Les codes 0..75 et
180..255 donneraient alors les mêmes 76 angles : ces angles seraient tirés
deux fois plus souvent que les 104 autres, la recherche serait biaisée. Le
rejet garde tous les angles équiprobables.
===============================================================================
"""

import numpy as np

import fitness as fit

# Constantes du codage d'un gène (= un pli)
BITS_PER_GENE = 8      # nombre de bits par angle
N_VALID_CODES = 180    # les codes 0..179 sont des angles, 180..255 sont rejetés
ANGLE_MIN = -89        # angle du code 0 [deg] ; le code 179 donne +90°


# =============================================================================
# 1. CONVERSIONS ENTRE BITS, CODES ET ANGLES
# =============================================================================
def bits_to_codes(pop_bits, n_plies):
    """
    Bits -> codes entiers.

    pop_bits : tableau de 0/1, forme (N, n_plies * 8), une ligne par individu.
    Renvoie  : tableau d'entiers dans [0, 255], forme (N, n_plies).
    """
    pop_size = pop_bits.shape[0]

    # On découpe chaque ligne de 160 bits en 20 paquets de 8 bits : forme (N, 20, 8)
    genes = pop_bits.reshape(pop_size, n_plies, BITS_PER_GENE)

    # Poids de chaque bit, du plus fort au plus faible : [128, 64, 32, 16, 8, 4, 2, 1]
    weights = 2 ** np.arange(BITS_PER_GENE - 1, -1, -1)

    # Code = somme(bit_j * poids_j). Exemple : [1,0,0,0,0,0,0,1] -> 128 + 1 = 129
    return genes @ weights


def codes_to_bits(codes):
    """
    Codes entiers -> bits (inverse de bits_to_codes).

    codes   : tableau d'entiers, forme (N, n_plies).
    Renvoie : tableau de 0/1 (int8), forme (N, n_plies * 8).
    """
    # Pour chaque code, le bit j (en partant du plus fort) vaut (code >> j) & 1 :
    # on décale le code de j crans vers la droite et on garde le dernier bit.
    # codes[..., None] ajoute un axe pour appliquer les 8 décalages à chaque code.
    shifts = np.arange(BITS_PER_GENE - 1, -1, -1)
    bits = (codes[..., None] >> shifts) & 1          # forme (N, n_plies, 8)
    return bits.reshape(codes.shape[0], -1).astype(np.int8)


def decode_population(pop_bits, n_plies):
    """
    Génotype (bits) -> phénotype (angles en degrés), forme (N, n_plies).
    Seuls des codes valides (0..179) sont présents dans la population.
    """
    return ANGLE_MIN + bits_to_codes(pop_bits, n_plies)


# =============================================================================
# 2. POPULATION INITIALE (P1 slide 48 : « N individus obtenus par tirage aléatoire »)
# =============================================================================
def init_population(pop_size, n_plies, rng):
    """
    Génération 0 aléatoire. Chaque gène est tiré uniformément parmi les 180
    codes valides : chaque angle a la même probabilité 1/180.
    Renvoie les bits, forme (pop_size, n_plies * 8).
    """
    codes = rng.integers(0, N_VALID_CODES, size=(pop_size, n_plies))
    return codes_to_bits(codes)


# =============================================================================
# 3. SÉLECTION : ROUE DE LOTERIE BIAISÉE (P2 slide 50)
# =============================================================================
def roulette_selection(pop_bits, fit_values, rng):
    """
    Tire N parents. L'individu i reçoit une part de roue proportionnelle à
    sa fitness f_i : P_i = f_i / somme(f_j). Les bons individus sont tirés
    plus souvent, les moins bons gardent une petite chance (sauf le pire,
    dont f = 0).
    """
    total = np.sum(fit_values)

    # Sécurité : si toutes les fitness sont nulles, tout le monde a la même chance
    if total == 0.0:
        probs = np.full(len(fit_values), 1.0 / len(fit_values))
    else:
        probs = fit_values / total

    # N tours de roue, avec remise : un très bon individu peut être choisi
    # plusieurs fois comme parent.
    indices = rng.choice(len(pop_bits), size=len(pop_bits), replace=True, p=probs)

    # .copy() pour que les opérateurs suivants ne modifient jamais l'ancienne population
    return pop_bits[indices].copy()


# =============================================================================
# 4. CROISEMENT : MÉLANGE DES GÉNOTYPES DES PARENTS (P1 slide 48)
# =============================================================================
def crossover_population(parents, p_crossover, rng, crossover_type="one_point"):
    """
    Les parents sont regroupés deux par deux : (0,1), (2,3), (4,5)...
    Avec la probabilité p_crossover (0,85), le couple échange une partie de
    ses bits pour faire 2 enfants ; sinon les enfants sont des copies des
    parents. L'enfant i commence toujours par les bits du parent i (c'est ce
    qu'utilise l'étape de rejet, qui se rabat sur le parent i).
    """
    children = parents.copy()
    pop_size, n_bits = parents.shape

    # Pas de 2 pour former les couples ; « pop_size - 1 » gère un pop_size impair
    for i in range(0, pop_size - 1, 2):
        if rng.random() < p_crossover:
            p1 = parents[i]
            p2 = parents[i + 1]

            if crossover_type == "one_point":
                # Un point de coupure « cut » entre 1 et 159 :
                #   enfant 1 = [début de P1] + [fin de P2]
                #   enfant 2 = [début de P2] + [fin de P1]
                cut = rng.integers(1, n_bits)
                children[i] = np.concatenate([p1[:cut], p2[cut:]])
                children[i + 1] = np.concatenate([p2[:cut], p1[cut:]])

            elif crossover_type == "two_point":
                # Deux points de coupure distincts c1 < c2 : seul le segment
                # du milieu [c1:c2] est échangé entre P1 et P2.
                c1, c2 = sorted(rng.choice(np.arange(1, n_bits), size=2, replace=False))
                children[i] = np.concatenate([p1[:c1], p2[c1:c2], p1[c2:]])
                children[i + 1] = np.concatenate([p2[:c1], p1[c1:c2], p2[c2:]])

            else:
                raise ValueError(f"Type de croisement inconnu : {crossover_type}")

    return children


# =============================================================================
# 5. MUTATION : MODIFICATION ALÉATOIRE DES GÈNES (P1 slide 53, P2 slide 50)
# =============================================================================
def mutate_population(pop_bits, p_mutation, n_plies, rng):
    """
    Garde de la diversité dans la population pour que l'AG ne reste pas
    bloqué.

    Comme dans le cours, la probabilité pm (= 1/N) s'applique à chaque GÈNE :
    chaque gène de chaque individu mute avec la probabilité pm, et une
    mutation inverse un bit tiré au hasard dans ce gène (0 <-> 1).
    """
    pop_size = pop_bits.shape[0]

    # True là où un gène mute, forme (N, n_plies)
    mask = rng.random((pop_size, n_plies)) < p_mutation

    # Numéro de ligne (individu) et numéro de gène de chaque gène qui mute
    rows, genes = np.nonzero(mask)

    # Position du bit inversé : premier bit du gène + décalage aléatoire 0..7
    bit_pos = genes * BITS_PER_GENE + rng.integers(0, BITS_PER_GENE, size=rows.size)

    mutated = pop_bits.copy()
    mutated[rows, bit_pos] = 1 - mutated[rows, bit_pos]   # 1 - 0 = 1, 1 - 1 = 0
    return mutated


# =============================================================================
# 6. REJET DES CODES INVALIDES (voir l'en-tête du fichier)
# =============================================================================
def reject_invalid_genes(children, parents, n_plies):
    """
    Tout gène d'un enfant dont le code est >= 180 (aucun angle) est rejeté :
    l'enfant reprend le gène de son parent au même endroit (parent i pour
    l'enfant i, toujours valide). Le croisement ou la mutation est donc
    annulé pour ce gène seulement.

    Renvoie les enfants corrigés et le nombre de gènes rejetés.
    """
    child_codes = bits_to_codes(children, n_plies)
    parent_codes = bits_to_codes(parents, n_plies)

    invalid = child_codes >= N_VALID_CODES
    child_codes[invalid] = parent_codes[invalid]

    return codes_to_bits(child_codes), int(invalid.sum())


# =============================================================================
# 7. ÉVALUATION D'UNE POPULATION
# =============================================================================
def evaluate_population(angles, Q, t_ply, objectives, K_A, K_D):
    """
    Coût Phi(delta) de chaque individu (une ligne d'angles chacun), calculé
    par fitness.cost. Plus il est proche de 0, meilleur est le stratifié.
    """
    return np.array([
        fit.cost(ind, Q, t_ply, objectives, K_A=K_A, K_D=K_D) for ind in angles
    ])


# =============================================================================
# 8. BOUCLE PRINCIPALE DE L'AG (P1 slide 48 : organigramme de l'AG standard)
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
    AG standard avec élitisme.

    Entrées principales (venant de config.py) :
    - Q                  : rigidité réduite 3x3 du pli [MPa]
    - t_ply              : épaisseur d'un pli [mm]
    - n_plies            : nombre de plis (20 pour le groupe 1)
    - objectives         : numéros des objectifs partiels ([1, 4, 9])
    - pop_size           : taille N de la population
    - n_generations      : critère d'arrêt Ngen
    - p_crossover        : probabilité de croisement pc
    - p_mutation         : probabilité de mutation pm, par gène
    - selection_pressure : exposant p de la fitness (énoncé : p = 1)
    - crossover_type     : "one_point" ou "two_point"
    - seed               : graine du hasard, pour des calculs reproductibles

    Renvoie un dictionnaire avec les meilleurs angles, le meilleur coût et
    l'historique (un dictionnaire de statistiques par génération).
    """
    rng = np.random.default_rng(seed)

    # Refuse les combinaisons d'objectifs qui n'ont pas de sens (voir fitness.py)
    fit.check_objectives(objectives)

    # --- GÉNÉRATION 0 : population aléatoire et son évaluation ---
    pop_bits = init_population(pop_size, n_plies, rng)
    angles = decode_population(pop_bits, n_plies)
    costs = evaluate_population(angles, Q, t_ply, objectives, K_A, K_D)
    n_rejected = 0          # aucun rejet pour la population initiale

    history = []

    for gen in range(n_generations):
        # A. On retient le meilleur individu de la génération courante (élitisme)
        best_idx = int(np.argmin(costs))
        best_bits = pop_bits[best_idx].copy()
        best_cost = float(costs[best_idx])

        # B. Statistiques de la population courante (CSV et courbe de convergence)
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
            print(f"Gen {gen + 1:3d}/{n_generations} | meilleur coût = {best_cost:.4e} | "
                  f"moyenne = {history[-1]['mean']:.4e}")

        # C. Fitness dans [0, 1] à partir des coûts (énoncé 2.a) :
        #    meilleur individu -> 1, pire individu -> 0
        fit_vals = fit.fitness(costs, p=selection_pressure)

        # D. Reproduction : sélection -> croisement -> mutation -> rejet
        parents = roulette_selection(pop_bits, fit_vals, rng)
        offspring = crossover_population(parents, p_crossover, rng, crossover_type)
        offspring = mutate_population(offspring, p_mutation, n_plies, rng)
        offspring, n_rejected = reject_invalid_genes(offspring, parents, n_plies)

        # E. Évaluation des enfants
        offspring_angles = decode_population(offspring, n_plies)
        offspring_costs = evaluate_population(offspring_angles, Q, t_ply, objectives, K_A, K_D)

        # F. Élitisme (P1 slide 48) : le pire enfant est remplacé par le
        #    meilleur individu de la génération précédente. La meilleure
        #    solution trouvée n'est donc jamais perdue.
        worst_idx = int(np.argmax(offspring_costs))
        offspring[worst_idx] = best_bits
        offspring_costs[worst_idx] = best_cost

        # G. Les enfants deviennent la génération courante
        pop_bits = offspring
        costs = offspring_costs
        angles = decode_population(pop_bits, n_plies)

    # --- FIN : meilleur individu de la dernière génération ---
    final_best_idx = int(np.argmin(costs))
    return {
        "best_angles": angles[final_best_idx],
        "best_cost": float(costs[final_best_idx]),
        "history": history,
    }
