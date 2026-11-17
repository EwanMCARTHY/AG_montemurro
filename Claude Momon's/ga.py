"""
===============================================================================
ALGORITHME GÉNÉTIQUE STANDARD À CODAGE BINAIRE (EVCSP - M. Montemurro)
===============================================================================
Référence cours : EVCSP_P1.pdf (slides 18 à 28) & EVCSP_P2.pdf (slide 50).
Contrainte      : Utilise uniquement NumPy comme bibliothèque externe.

Principe général du codage :
----------------------------
On cherche 20 angles d'orientation de plis dans ]-90°, 90°] au pas de 1°,
soit 180 valeurs entières possibles : -89°, -88°, ..., 0°, ..., +89°, +90°.

En binaire :
- 7 bits permettent seulement 2^7 = 128 valeurs (insuffisant pour 180 angles).
- 8 bits permettent 2^8 = 256 valeurs (de 0 à 255). On choisit donc 8 bits/pli.
- Un "individu" (un stratifié complet de 20 plis) est donc représenté par une
  chaîne de 20 * 8 = 160 bits (des 0 et des 1) appelée "chromosome".
===============================================================================
"""

import numpy as np
import fitness as fit  # Module interne du projet (qui n'utilise lui-même que NumPy)

# Constantes de codage binaire d'un gène (= 1 pli)
BITS_PER_GENE = 8      # Nombre de bits par angle (2^8 = 256 combinaisons possibles)
ANGLE_MIN = -89.0      # Plus petit angle autorisé dans ]-90°, 90°] au pas de 1°
ANGLE_MAX = 90.0       # Plus grand angle autorisé


# =============================================================================
# 1. DÉCODAGE : PASSAGE DU GÉNOTYPE (BITS) AU PHÉNOTYPE (ANGLES EN DEGRÉS)
# =============================================================================
def decode_population(pop_bits, n_plies):
    """
    Transforme toute la population binaire en matrice d'angles en degrés.

    Paramètres
    ----------
    pop_bits : tableau NumPy d'entiers (0 ou 1) de forme (N, n_plies * 8)
               Chaque ligne = 1 individu (160 bits).
    n_plies  : int, nombre de plis du stratifié (20 pour le Groupe 1).

    Retourne
    --------
    angles   : tableau NumPy de flottants de forme (N, n_plies)
               Chaque ligne = les 20 angles en degrés d'un individu.
    """
    pop_size = pop_bits.shape[0]  # N = nombre d'individus dans la population

    # Étape A : On découpe la chaîne de 160 bits en 20 paquets de 8 bits.
    # La forme passe de (N, 160) à (N, 20, 8).
    genes = pop_bits.reshape(pop_size, n_plies, BITS_PER_GENE)

    # Étape B : On convertit chaque paquet de 8 bits en un entier entre 0 et 255.
    # Les poids binaires sont [128, 64, 32, 16, 8, 4, 2, 1].
    weights = 2 ** np.arange(BITS_PER_GENE - 1, -1, -1)

    # Produit matriciel (@) sur le dernier axe : somme(bit_j * poids_j).
    # Exemple : [1, 0, 0, 0, 0, 0, 0, 1] -> 128 + 1 = 129.
    # Résultat "ints" de forme (N, 20) contenant des entiers dans [0, 255].
    ints = genes @ weights

    # Étape C : Mapping linéaire de [0, 255] vers [-89°, +90°].
    # - Si int = 0   -> -89 + round(0)   = -89°
    # - Si int = 255 -> -89 + round(179) = +90°
    # L'arrondi np.round(...) garantit des angles entiers (pas de 1°).
    # Avantage : TOUTE suite de 8 bits donne un angle valide, sans valeur interdite.
    angles = ANGLE_MIN + np.round((ints / 255.0) * (ANGLE_MAX - ANGLE_MIN))
    return angles


# =============================================================================
# 2. INITIALISATION : CRÉATION DE LA POPULATION DE DÉPART
# =============================================================================
def init_population(pop_size, n_plies, rng):
    """
    Génère aléatoirement la génération 0 (P1 slide 19).

    Chaque bit est tiré à pile ou face (0 ou 1 équiprobables).
    Retourne un tableau de forme (pop_size, n_plies * 8).
    """
    n_bits = n_plies * BITS_PER_GENE
    # rng.integers(0, 2, ...) tire des entiers dans {0, 1} (borne haute 2 exclue).
    # dtype=np.int8 économise la mémoire (1 octet par bit au lieu de 8).
    return rng.integers(0, 2, size=(pop_size, n_bits), dtype=np.int8)


# =============================================================================
# 3. SÉLECTION : ROUE DE LOTERIE BIAISÉE (P1 slide 22)
# =============================================================================
def roulette_selection(pop_bits, fit_values, rng):
    """
    Sélectionne N parents pour la reproduction.
    Plus un individu a une fitness f_i élevée, plus sa part de la roulette
    est grande, et plus il a de chances d'être tiré (mais les moins bons
    gardent une petite chance de transmettre des gènes utiles).
    """
    total = np.sum(fit_values)

    # Sécurité : si tous les individus ont une fitness nulle (très rare),
    # on donne à chacun la même probabilité 1/N pour éviter une division par 0.
    if total == 0.0:
        probs = np.full(len(fit_values), 1.0 / len(fit_values))
    else:
        # Probabilité de sélection du i-ème individu : P_i = f_i / somme(f_j)
        probs = fit_values / total

    # On fait tourner la roue N fois (tirage AVEC remise : replace=True).
    # Un très bon individu peut donc être choisi plusieurs fois comme parent.
    indices = rng.choice(len(pop_bits), size=len(pop_bits), replace=True, p=probs)

    # .copy() est crucial pour ne pas modifier les individus d'origine par mégarde.
    return pop_bits[indices].copy()


# =============================================================================
# 4. CROISEMENT (CROSS-OVER) : MÉLANGE DES GÉNOTYPES DES PARENTS (P1 slide 23)
# =============================================================================
def crossover_population(parents, p_crossover, rng, crossover_type="one_point"):
    """
    Regroupe les parents deux par deux : (0,1), (2,3), (4,5)...
    Avec une probabilité p_crossover (ex: 85%), on mélange leurs chromosomes
    binaires pour créer 2 enfants. Sinon (15%), les enfants sont des clones
    exacts des 2 parents.
    """
    children = parents.copy()
    pop_size, n_bits = parents.shape

    # On avance par pas de 2 (i = 0, 2, 4, ...) pour former les couples.
    # "pop_size - 1" évite un crash si jamais pop_size est impair.
    for i in range(0, pop_size - 1, 2):
        # Tirage d'un nombre dans [0, 1[ : si < 0.85, il y a croisement.
        if rng.random() < p_crossover:
            p1 = parents[i]
            p2 = parents[i + 1]

            if crossover_type == "one_point":
                # Croisement en 1 point (illustré P1 slide 23) :
                # On choisit une coupure aléatoire "cut" entre 1 et 159.
                # Enfant 1 = [début de P1] + [fin de P2]
                # Enfant 2 = [début de P2] + [fin de P1]
                cut = rng.integers(1, n_bits)
                children[i] = np.concatenate([p1[:cut], p2[cut:]])
                children[i + 1] = np.concatenate([p2[:cut], p1[cut:]])

            elif crossover_type == "two_point":
                # Croisement en 2 points :
                # On tire 2 coupures distinctes c1 < c2 (replace=False).
                # On échange uniquement le segment central [c1:c2] entre P1 et P2.
                # Utile pour les stratifiés car les plis externes (haut & bas)
                # restent groupés ensemble.
                c1, c2 = sorted(rng.choice(np.arange(1, n_bits), size=2, replace=False))
                children[i] = np.concatenate([p1[:c1], p2[c1:c2], p1[c2:]])
                children[i + 1] = np.concatenate([p2[:c1], p1[c1:c2], p2[c2:]])

            else:
                raise ValueError(f"Type de croisement inconnu : {crossover_type}")

    return children


# =============================================================================
# 5. MUTATION : ALTÉRATION STOCHASTIQUE DES BITS (P1 slide 24)
# =============================================================================
def mutate_population(pop_bits, p_mutation, rng):
    """
    Maintient la biodiversité dans la population pour éviter que l'AG ne reste
    bloqué dans un minimum local (convergence prématurée).

    Chaque bit de toute la matrice (N x 160) a une petite probabilité pm
    (ex: 1/500 = 0.002) d'être inversé : 0 devient 1, et 1 devient 0.
    """
    # On tire un tableau de nombres aléatoires entre 0 et 1 de même taille que pop_bits.
    # "mask" vaut True là où le tirage est inférieur à p_mutation.
    mask = rng.random(pop_bits.shape) < p_mutation

    mutated = pop_bits.copy()
    # Astuce mathématique pour inverser un bit : 1 - 0 = 1 et 1 - 1 = 0.
    mutated[mask] = 1 - mutated[mask]
    return mutated


# =============================================================================
# 6. FONCTION UTILITAIRE D'ÉVALUATION
# =============================================================================
def _evaluate_population(angles, Q, t_ply, objectives, K_A, K_D):
    """
    Calcule le coût Phi(delta) de chaque individu (stratifié de 20 angles)
    en appelant fit.cost() du module fitness.py.
    Rappel : plus le coût Phi est proche de 0, meilleur est le stratifié.
    """
    return np.array([
        fit.cost(ind, Q, t_ply, objectives, K_A=K_A, K_D=K_D) for ind in angles
    ])


# =============================================================================
# 7. BOUCLE PRINCIPALE DE L'ALGORITHME GÉNÉTIQUE (P1 slides 19 & 25)
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
    Exécute l'AG standard avec élitisme (P1 slides 19 & 25).

    Paramètres principaux (issus de config.py) :
    - Q                  : matrice 3x3 de rigidité réduite du pli de base [MPa]
    - t_ply              : épaisseur d'un pli [mm]
    - n_plies            : nombre de plis (20 pour le Groupe 1)
    - objectives         : liste des indices d'objectifs partiels ([1, 4, 9])
    - pop_size           : taille N de la population (500)
    - n_generations      : critère d'arrêt Ngen (500)
    - p_crossover        : probabilité pc de croisement (0.85)
    - p_mutation         : probabilité pm de mutation par bit (1/500 = 0.002)
    - selection_pressure : exposant p de la fitness (1.0)
    - crossover_type     : "one_point" ou "two_point"
    - seed               : graine aléatoire pour rendre les résultats reproductibles
    """
    # Initialisation du générateur de nombres aléatoires NumPy
    rng = np.random.default_rng(seed)

    # Vérifie que la liste d'objectifs (ex: [1, 4, 9]) est cohérente
    fit.check_objectives(objectives)

    # --- GÉNÉRATION 0 : Création et évaluation de la population initiale ---
    pop_bits = init_population(pop_size, n_plies, rng)
    angles = decode_population(pop_bits, n_plies)
    costs = _evaluate_population(angles, Q, t_ply, objectives, K_A, K_D)

    # Liste qui stockera l'évolution des statistiques à chaque génération
    history = []

    # --- BOUCLE D'ÉVOLUTION SUR N_GENERATIONS ---
    for gen in range(n_generations):
        # A. Sauvegarde du meilleur individu de la génération courante (pour l'élitisme)
        best_idx = int(np.argmin(costs))       # Indice du coût le plus petit
        best_bits = pop_bits[best_idx].copy()  # Son chromosome binaire
        best_cost = float(costs[best_idx])     # Sa valeur de fonction de coût Phi

        # B. Enregistrement des statistiques (pour tracer la courbe de convergence)
        history.append({
            "generation": gen,
            "min": best_cost,
            "mean": float(np.mean(costs)),
            "max": float(np.max(costs)),
            "std": float(np.std(costs)),
        })

        # Affichage périodique dans le terminal pour suivre la progression
        if verbose and (gen == 0 or (gen + 1) % 50 == 0):
            print(
                f"Gen {gen + 1:3d}/{n_generations} | "
                f"Meilleur coût = {best_cost:.4e} | "
                f"Moyenne = {history[-1]['mean']:.4e}"
            )

        # C. Calcul de l'adaptation (fitness) dans [0, 1] à partir des coûts
        # Meilleur individu -> fitness = 1 ; pire individu -> fitness = 0
        fit_vals = fit.fitness(costs, p=selection_pressure)

        # D. Reproduction : Sélection -> Croisement -> Mutation
        parents = roulette_selection(pop_bits, fit_vals, rng)
        offspring = crossover_population(parents, p_crossover, rng, crossover_type=crossover_type)
        offspring = mutate_population(offspring, p_mutation, rng)

        # E. Évaluation des enfants (nouvelle génération)
        offspring_angles = decode_population(offspring, n_plies)
        offspring_costs = _evaluate_population(offspring_angles, Q, t_ply, objectives, K_A, K_D)

        # F. Élitisme (P1 slide 25) :
        # On cherche le pire individu parmi les enfants (coût maximal) et on le
        # remplace par le meilleur individu sauvegardé de la génération précédente.
        # Cela garantit que la meilleure solution trouvée ne soit jamais perdue !
        worst_idx = int(np.argmax(offspring_costs))
        offspring[worst_idx] = best_bits
        offspring_costs[worst_idx] = best_cost

        # G. La nouvelle génération devient la génération courante pour l'itération suivante
        pop_bits = offspring
        costs = offspring_costs

    # --- FIN DE L'ALGORITHME : Extraction du meilleur individu final ---
    final_best_idx = int(np.argmin(costs))
    # On passe [final_best_idx:final_best_idx + 1] pour garder une forme 2D (1, 160)
    best_angles = decode_population(pop_bits[final_best_idx:final_best_idx + 1], n_plies)[0]

    return {
        "best_angles": best_angles,
        "best_cost": float(costs[final_best_idx]),
        "history": history,
    }
