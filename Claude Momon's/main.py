"""
===============================================================================
SCRIPT PRINCIPAL DU PROJET (EVCSP - Groupe 1 - M. Montemurro)
===============================================================================
Ce fichier orchestre l'exécution complète du programme :
1. Lecture des données d'entrée dans config.py.
2. Calcul des matrices S et Q du pli de base (laminate.py).
3. Lancement de l'algorithme génétique (ga.py).
4. Calcul détaillé du meilleur stratifié trouvé (matrices A*, B*, D*, C et
   paramètres polaires associés).
5. Export des résultats dans le dossier 'results/' :
   - ga_statistics.csv  : statistiques par génération (séparateur ';', UTF-8 BOM)
   - best_laminate.txt  : angles optimaux, coûts et paramètres polaires
   - convergence.png    : courbe de convergence et écart-type
   - polar_diagrams.png : diagrammes polaires de Q, A* et D*

Usage dans un terminal (depuis le dossier "Claude Momon's") :
    python main.py
    python main.py --crossover two_point
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


def save_statistics_csv(history, out_dir):
    """
    Sauvegarde les statistiques de chaque génération dans 'ga_statistics.csv'.
    Encodage 'utf-8-sig' (UTF-8 avec BOM) et séparateur ';' pour une ouverture
    directe et propre dans Excel en français.
    """
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "ga_statistics.csv")

    fieldnames = ["generation", "min", "mean", "max", "std"]
    with open(csv_path, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(history)

    return csv_path


def save_best_laminate_txt(
    best_angles,
    best_cost,
    Q,
    A_star,
    B_star,
    D_star,
    C,
    pp_ply,
    pp_A,
    pp_B,
    pp_D,
    pp_C,
    phi_dict,
    crossover_type,
    out_dir,
):
    """
    Rédige un résumé complet et lisible du meilleur stratifié trouvé dans
    'best_laminate.txt' (angles, fonction de coût, paramètres polaires et
    matrices homogénéisées).
    """
    os.makedirs(out_dir, exist_ok=True)
    txt_path = os.path.join(out_dir, "best_laminate.txt")

    def _fmt_polar(pp):
        return (
            f"T0={pp['T0']:.2f} MPa, T1={pp['T1']:.2f} MPa, "
            f"R0={pp['R0']:.2f} MPa, R1={pp['R1']:.2f} MPa, "
            f"Phi0={np.degrees(pp['Phi0']):.2f} deg, Phi1={np.degrees(pp['Phi1']):.2f} deg"
        )

    with open(txt_path, mode="w", encoding="utf-8") as f:
        f.write("====================================================================\n")
        f.write(f"PROJET EVCSP - GROUPE {config.GROUP} ({config.N_PLIES} plis)\n")
        f.write(f"Croisement utilisé : {crossover_type}\n")
        f.write("====================================================================\n\n")

        angles_list = [int(round(a)) for a in best_angles]
        f.write("1. SÉQUENCE D'EMPILEMENT OPTIMALE (du pli 1 en bas au pli 20 en haut) [deg] :\n")
        f.write(f"   {angles_list}\n\n")

        f.write("2. FONCTION DE COÛT ET OBJECTIFS PARTIELS :\n")
        f.write(f"   Coût total Phi(delta) = {best_cost:.6e}\n")
        for idx in config.OBJECTIVES:
            f.write(f"   - Phi_{idx} = {phi_dict[idx]:.6e}\n")
        f.write("\n")

        f.write("3. PARAMÈTRES POLAIRES :\n")
        f.write(f"   Pli Q : {_fmt_polar(pp_ply)}\n")
        f.write(f"   A*    : {_fmt_polar(pp_A)}\n")
        f.write(f"   B*    : {_fmt_polar(pp_B)}\n")
        f.write(f"   D*    : {_fmt_polar(pp_D)}\n")
        f.write(f"   C     : {_fmt_polar(pp_C)}\n\n")

        np.set_printoptions(precision=2, suppress=True)
        f.write("4. MATRICES HOMOGÉNÉISÉES CARTÉSIENNES [MPa] :\n")
        f.write(f"   [A*] =\n{A_star}\n\n")
        f.write(f"   [B*] =\n{B_star}\n\n")
        f.write(f"   [D*] =\n{D_star}\n")

    return txt_path


def main():
    # --- 1. Gestion des options en ligne de commande ---
    parser = argparse.ArgumentParser(
        description="Optimisation d'empilement composite (EVCSP Groupe 1)."
    )
    parser.add_argument(
        "--crossover",
        choices=["one_point", "two_point"],
        default="one_point",
        help="Type de croisement binaire : 'one_point' (défaut) ou 'two_point'.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=config.SEED,
        help="Graine aléatoire pour la reproductibilité.",
    )
    args = parser.parse_args()

    # --- 2. Propriétés mécaniques du pli élémentaire ---
    S = lam.ply_compliance(config.E1, config.E2, config.NU12, config.G12)
    Q = lam.ply_stiffness(S)

    print("====================================================================")
    print(f"Lancement de l'AG - Groupe {config.GROUP} ({config.N_PLIES} plis)")
    print(f"Population = {config.POP_SIZE} | Générations = {config.N_GENERATIONS}")
    print(f"Croisement = {args.crossover} (pc={config.P_CROSSOVER}) | pm = {config.P_MUTATION}")
    print("====================================================================")

    # --- 3. Exécution de l'algorithme génétique ---
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

    # --- 4. Post-traitement mécanique du meilleur stratifié ---
    A_star, B_star, D_star, C = lam.laminate_matrices(Q, best_angles, config.T_PLY)
    pp_ply = pol.polar_parameters(Q)
    pp_A = pol.polar_parameters(A_star)
    pp_B = pol.polar_parameters(B_star)
    pp_D = pol.polar_parameters(D_star)
    pp_C = pol.polar_parameters(C)
    phi_dict = fit.partial_objectives(
        pp_A, pp_B, pp_D, pp_C, pp_ply, K_A=config.K_A, K_D=config.K_D
    )

    # --- 5. Sauvegarde des fichiers et des graphiques dans results/ ---
    out_dir = config.RESULTS_DIR
    csv_path = save_statistics_csv(history, out_dir)
    txt_path = save_best_laminate_txt(
        best_angles, best_cost, Q, A_star, B_star, D_star, C,
        pp_ply, pp_A, pp_B, pp_D, pp_C, phi_dict, args.crossover, out_dir,
    )
    conv_path = plots.plot_convergence(history, out_dir)
    polar_path = plots.plot_polar_diagrams(Q, A_star, D_star, out_dir)

    # --- 6. Résumé final dans le terminal ---
    print("\n====================================================================")
    print("OPTIMISATION TERMINÉE")
    print(f"Meilleur coût Phi : {best_cost:.6e}")
    print(f"Empilement optimal : {[int(round(a)) for a in best_angles]}")
    print("Fichiers générés :")
    print(f"  - {csv_path}")
    print(f"  - {txt_path}")
    print(f"  - {conv_path}")
    print(f"  - {polar_path}")
    print("====================================================================")


if __name__ == "__main__":
    main()
