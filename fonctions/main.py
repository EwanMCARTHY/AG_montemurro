"""
===============================================================================
SCRIPT PRINCIPAL (EVCSP - Groupe 1 - M. Montemurro)
===============================================================================
Enchaîne tout le projet :
1. lit les données d'entrée dans config.py ;
2. calcule les matrices S et Q du pli (laminate.py) ;
3. lance l'algorithme génétique (ga.py) ;
4. calcule A*, B*, D* pour le meilleur stratifié ;
5. écrit les résultats dans results/seed_<graine>/ (à côté de ce fichier) :
   - ga_statistics.csv  : statistiques par génération (séparateur ';', UTF-8 avec BOM)
   - convergence.svg/.pdf/.png
   - polar_diagrams.svg/.pdf/.png

Utilisation (depuis le dossier "fonctions") :
    ../.venv/Scripts/python main.py
    ../.venv/Scripts/python main.py --crossover two_point --seed 3
===============================================================================
"""

import argparse
import csv
import os

import config
import ga
import laminate as lam
import plots

# Dossier des résultats à côté de ce fichier, quel que soit le dossier d'où
# on lance le script
HERE = os.path.dirname(os.path.abspath(__file__))


# =============================================================================
# 1. CSV DES STATISTIQUES DE LA POPULATION
# =============================================================================
def save_statistics_csv(history, out_dir):
    """
    Une ligne par génération. Encodage 'utf-8-sig' (UTF-8 avec BOM) et
    séparateur ';' pour qu'Excel (réglages français) l'ouvre directement en
    colonnes.
    """
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "ga_statistics.csv")

    fieldnames = ["generation", "min", "mean", "median", "max", "std",
                  "rejected_genes", "best_stacking"]
    with open(csv_path, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(history)
    return csv_path


# =============================================================================
# 2. PROGRAMME PRINCIPAL
# =============================================================================
def main():
    # --- Options de la ligne de commande ---
    parser = argparse.ArgumentParser(description="Optimisation d'empilement (EVCSP groupe 1).")
    parser.add_argument("--crossover", choices=["one_point", "two_point"],
                        default="one_point", help="type de croisement (défaut : one_point)")
    parser.add_argument("--seed", type=int, default=config.SEED,
                        help="graine du hasard, pour des calculs reproductibles")
    args = parser.parse_args()

    # Un dossier par graine, pour ne pas écraser les calculs précédents
    out_dir = os.path.join(HERE, config.RESULTS_DIR, f"seed_{args.seed}")

    # --- Pli : souplesse S et rigidité réduite Q ---
    S = lam.ply_compliance(config.E1, config.E2, config.NU12, config.G12)
    Q = lam.ply_stiffness(S)

    print("=" * 68)
    print(f"Calcul AG - groupe {config.GROUP} ({config.N_PLIES} plis), "
          f"objectifs {config.OBJECTIVES}, graine {args.seed}")
    print(f"N = {config.POP_SIZE} | Ngen = {config.N_GENERATIONS} | "
          f"croisement = {args.crossover} (pc = {config.P_CROSSOVER}) | pm = {config.P_MUTATION:g}")
    print("=" * 68)

    # --- Algorithme génétique ---
    result = ga.run_ga(
        Q=Q,
        t_ply=config.T_PLY,
        n_plies=config.N_PLIES,
        objectives=config.OBJECTIVES,
        pop_size=config.POP_SIZE,
        n_generations=config.N_GENERATIONS,
        p_crossover=config.P_CROSSOVER,
        p_mutation=config.P_MUTATION,
        selection_pressure=config.SELECTION_PRESSURE,
        K_A=config.K_A,
        K_D=config.K_D,
        crossover_type=args.crossover,
        seed=args.seed,
        verbose=True,
    )
    best_angles = result["best_angles"]
    best_cost = result["best_cost"]
    history = result["history"]

    # --- Matrices du meilleur stratifié, pour les diagrammes polaires ---
    A_star, B_star, D_star, _ = lam.laminate_matrices(Q, best_angles, config.T_PLY)

    # --- Fichiers et figures ---
    written = [save_statistics_csv(history, out_dir)]
    written += plots.plot_convergence(history, out_dir)
    written += plots.plot_polar_diagrams(Q, A_star, B_star, D_star, out_dir)

    # --- Résumé dans le terminal ---
    print("\n" + "=" * 68)
    print("OPTIMISATION TERMINÉE")
    print(f"Meilleur coût Phi : {best_cost:.6e}")
    print("Meilleur empilement : [" + "/".join(str(int(a)) for a in best_angles) + "]")
    print("Fichiers écrits :")
    for path in written:
        print(f"  - {os.path.relpath(path, HERE)}")
    print("=" * 68)


if __name__ == "__main__":
    main()
