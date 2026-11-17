"""
===============================================================================
MAIN SCRIPT (EVCSP - Group 1 - M. Montemurro)
===============================================================================
Runs the whole project:
1. reads the input data in config.py;
2. computes the ply matrices S and Q (laminate.py);
3. runs the genetic algorithm (ga.py);
4. computes A*, B*, D*, C and their polar parameters for the best laminate;
5. writes the results to results/ (next to this file):
   - ga_statistics.csv  : statistics per generation (';' separator, UTF-8 BOM)
   - best_laminate.txt  : best stacking, costs and polar parameters
   - convergence.svg/.pdf/.png
   - polar_diagrams.svg/.pdf/.png

Usage (from the "Claude Momon's" folder):
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

# Results folder next to this file, whatever the folder the script is run from
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, config.RESULTS_DIR)


# =============================================================================
# 1. CSV OF THE POPULATION STATISTICS
# =============================================================================
def save_statistics_csv(history, out_dir):
    """
    One row per generation. Encoding 'utf-8-sig' (UTF-8 with BOM) and ';'
    separator, so that Excel (French settings) opens it directly in columns.
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
# 2. TEXT SUMMARY OF THE BEST LAMINATE
# =============================================================================
def save_best_laminate_txt(best_angles, best_cost, matrices, polar_params,
                           phi_dict, crossover_type, seed, out_dir):
    """
    Writes best_laminate.txt: stacking, cost and partial objectives, polar
    parameters, homogenised Cartesian matrices.

    matrices     : dict {"A*": ..., "B*": ..., "D*": ...}
    polar_params : dict {"Q": ..., "A*": ..., "B*": ..., "D*": ..., "C": ...}
    """
    os.makedirs(out_dir, exist_ok=True)
    txt_path = os.path.join(out_dir, "best_laminate.txt")

    def fmt_polar(pp):
        """One line with the six polar parameters (angles in degrees)."""
        return (f"T0={pp['T0']:.2f} MPa, T1={pp['T1']:.2f} MPa, "
                f"R0={pp['R0']:.4f} MPa, R1={pp['R1']:.4f} MPa, "
                f"Phi0={np.degrees(pp['Phi0']):.2f} deg, Phi1={np.degrees(pp['Phi1']):.2f} deg")

    with open(txt_path, mode="w", encoding="utf-8") as f:
        f.write("=" * 68 + "\n")
        f.write(f"EVCSP PROJECT - GROUP {config.GROUP} ({config.N_PLIES} plies)\n")
        f.write(f"Crossover: {crossover_type} | seed: {seed} | "
                f"N = {config.POP_SIZE} | Ngen = {config.N_GENERATIONS}\n")
        f.write("=" * 68 + "\n\n")

        f.write("1. BEST STACKING SEQUENCE (ply 1 at the bottom, z = -h/2) [deg]:\n")
        f.write("   [" + "/".join(str(int(a)) for a in best_angles) + "]\n\n")

        f.write("2. COST FUNCTION AND PARTIAL OBJECTIVES:\n")
        f.write(f"   Phi(delta) = {best_cost:.6e}\n")
        for idx in config.OBJECTIVES:
            f.write(f"   - Phi{idx} = {phi_dict[idx]:.6e}\n")
        f.write("\n")

        f.write("3. POLAR PARAMETERS (angles are meaningless when R = 0):\n")
        for name, pp in polar_params.items():
            f.write(f"   {name:<3}: {fmt_polar(pp)}\n")
        f.write("\n")

        f.write("4. HOMOGENISED CARTESIAN MATRICES [MPa]:\n")
        for name, M in matrices.items():
            f.write(f"   [{name}] =\n{np.array2string(M, precision=2, suppress_small=True)}\n\n")
    return txt_path


# =============================================================================
# 3. MAIN PROGRAM
# =============================================================================
def main():
    # --- Command-line options ---
    parser = argparse.ArgumentParser(description="Stacking optimisation (EVCSP group 1).")
    parser.add_argument("--crossover", choices=["one_point", "two_point"],
                        default="one_point", help="crossover type (default: one_point)")
    parser.add_argument("--seed", type=int, default=config.SEED,
                        help="random seed, for reproducible runs")
    args = parser.parse_args()

    # --- Ply: compliance S and reduced stiffness Q ---
    S = lam.ply_compliance(config.E1, config.E2, config.NU12, config.G12)
    Q = lam.ply_stiffness(S)

    print("=" * 68)
    print(f"GA run - group {config.GROUP} ({config.N_PLIES} plies), "
          f"objectives {config.OBJECTIVES}")
    print(f"N = {config.POP_SIZE} | Ngen = {config.N_GENERATIONS} | "
          f"crossover = {args.crossover} (pc = {config.P_CROSSOVER}) | pm = {config.P_MUTATION:g}")
    print("=" * 68)

    # --- Genetic algorithm ---
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

    # --- Mechanics of the best laminate ---
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

    # --- Files and figures ---
    written = [save_statistics_csv(history, OUT_DIR)]
    written.append(save_best_laminate_txt(
        best_angles, best_cost, {"A*": A_star, "B*": B_star, "D*": D_star},
        polar_params, phi_dict, args.crossover, args.seed, OUT_DIR,
    ))
    written += plots.plot_convergence(history, OUT_DIR)
    written += plots.plot_polar_diagrams(Q, A_star, B_star, D_star, OUT_DIR)

    # --- Summary in the terminal ---
    print("\n" + "=" * 68)
    print("OPTIMISATION FINISHED")
    print(f"Best cost Phi : {best_cost:.6e}")
    print("Best stacking : [" + "/".join(str(int(a)) for a in best_angles) + "]")
    print("Files written :")
    for path in written:
        print(f"  - {os.path.relpath(path, HERE)}")
    print("=" * 68)


if __name__ == "__main__":
    main()
