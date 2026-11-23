"""
===============================================================================
SCRIPT PRINCIPAL (EVCSP - Groupe 1 - M. Montemurro)
===============================================================================
Enchaîne tout le projet :
1. lit les données d'entrée dans config.py ;
2. calcule les matrices S et Q du pli (laminate.py) ;
3. lance l'algorithme génétique (ga.py) ;
4. calcule A*, B*, D*, C et leurs paramètres polaires pour le meilleur stratifié ;
5. écrit les résultats dans results/ (à côté de ce fichier) :
   - ga_statistics.csv  : statistiques par génération (séparateur ';', UTF-8 avec BOM)
   - best_laminate.txt  : meilleur empilement, coûts et paramètres polaires
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

import numpy as np

import config
import fitness as fit
import ga
import laminate as lam
import plots
import polar as pol

# Dossier des résultats à côté de ce fichier, quel que soit le dossier d'où
# on lance le script
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, config.RESULTS_DIR)


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
# 2. RÉSUMÉ TEXTE DU MEILLEUR STRATIFIÉ
# =============================================================================
def save_best_laminate_txt(best_angles, best_cost, matrices, polar_params,
                           phi_dict, crossover_type, seed, out_dir):
    """
    Écrit best_laminate.txt : empilement, coût et objectifs partiels,
    paramètres polaires, matrices cartésiennes homogénéisées.

    matrices     : dictionnaire {"A*": ..., "B*": ..., "D*": ...}
    polar_params : dictionnaire {"Q": ..., "A*": ..., "B*": ..., "D*": ..., "C": ...}
    """
    os.makedirs(out_dir, exist_ok=True)
    txt_path = os.path.join(out_dir, "best_laminate.txt")

    def fmt_polar(pp):
        """Une ligne avec les six paramètres polaires (angles en degrés)."""
        return (f"T0={pp['T0']:.2f} MPa, T1={pp['T1']:.2f} MPa, "
                f"R0={pp['R0']:.4f} MPa, R1={pp['R1']:.4f} MPa, "
                f"Phi0={np.degrees(pp['Phi0']):.2f} deg, Phi1={np.degrees(pp['Phi1']):.2f} deg")

    with open(txt_path, mode="w", encoding="utf-8") as f:
        f.write("=" * 68 + "\n")
        f.write(f"PROJET EVCSP - GROUPE {config.GROUP} ({config.N_PLIES} plis)\n")
        f.write(f"Croisement : {crossover_type} | graine : {seed} | "
                f"N = {config.POP_SIZE} | Ngen = {config.N_GENERATIONS}\n")
        f.write("=" * 68 + "\n\n")

        f.write("1. MEILLEUR EMPILEMENT (pli 1 en bas, z = -h/2) [deg] :\n")
        f.write("   [" + "/".join(str(int(a)) for a in best_angles) + "]\n\n")

        f.write("2. FONCTION DE COÛT ET OBJECTIFS PARTIELS :\n")
        f.write(f"   Phi(delta) = {best_cost:.6e}\n")
        for idx in config.OBJECTIVES:
            f.write(f"   - Phi{idx} = {phi_dict[idx]:.6e}\n")
        f.write("\n")

        f.write("3. PARAMÈTRES POLAIRES (les angles n'ont pas de sens quand R = 0) :\n")
        for name, pp in polar_params.items():
            f.write(f"   {name:<3}: {fmt_polar(pp)}\n")
        f.write("\n")

        f.write("4. MATRICES CARTÉSIENNES HOMOGÉNÉISÉES [MPa] :\n")
        for name, M in matrices.items():
            f.write(f"   [{name}] =\n{np.array2string(M, precision=2, suppress_small=True)}\n\n")
    return txt_path


# =============================================================================
# 3. PROGRAMME PRINCIPAL
# =============================================================================
def main():
    # --- Options de la ligne de commande ---
    parser = argparse.ArgumentParser(description="Optimisation d'empilement (EVCSP groupe 1).")
    parser.add_argument("--crossover", choices=["one_point", "two_point"],
                        default="one_point", help="type de croisement (défaut : one_point)")
    parser.add_argument("--seed", type=int, default=config.SEED,
                        help="graine du hasard, pour des calculs reproductibles")
    args = parser.parse_args()

    # --- Pli : souplesse S et rigidité réduite Q ---
    S = lam.ply_compliance(config.E1, config.E2, config.NU12, config.G12)
    Q = lam.ply_stiffness(S)

    print("=" * 68)
    print(f"Calcul AG - groupe {config.GROUP} ({config.N_PLIES} plis), "
          f"objectifs {config.OBJECTIVES}")
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

    # --- Mécanique du meilleur stratifié ---
    A_star, B_star, D_star, C = lam.laminate_matrices(Q, best_angles, config.T_PLY)
    polar_params = {
        "Q": pol.polar_parameters(Q),
        "A*": pol.polar_parameters(A_star),
        "B*": pol.polar_parameters(B_star),
        "D*": pol.polar_parameters(D_star),
        "C": pol.polar_parameters(C),
    }
    phi_dict = fit.partial_objectives(
        polar_params["A*"], polar_params["B*"], polar_params["D*"], polar_params["C"],
        polar_params["Q"], K_A=config.K_A, K_D=config.K_D,
    )

    # --- Fichiers et figures ---
    written = [save_statistics_csv(history, OUT_DIR)]
    written.append(save_best_laminate_txt(
        best_angles, best_cost, {"A*": A_star, "B*": B_star, "D*": D_star},
        polar_params, phi_dict, args.crossover, args.seed, OUT_DIR,
    ))
    written += plots.plot_convergence(history, OUT_DIR)
    written += plots.plot_polar_diagrams(Q, A_star, B_star, D_star, OUT_DIR)

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
