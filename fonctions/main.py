"""
Script principal : calcule Q, lance l'AG, puis écrit dans results/seed_<graine>/ :
- ga_statistics.csv  : statistiques de la population par génération (séparateur ';')
- convergence.png et polar_diagrams.png

Utilisation (depuis le dossier "fonctions") :
    ../.venv/Scripts/python main.py --seed 2
"""

import argparse
import csv
import os

import config
import ga
import laminate as lam
import plots

# --- Graine choisie en ligne de commande (défaut : config.SEED) ---
parser = argparse.ArgumentParser()
parser.add_argument("--seed", type=int, default=config.SEED)
seed = parser.parse_args().seed

# Un dossier de résultats par graine, à côté de ce fichier
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", f"seed_{seed}")
os.makedirs(out_dir, exist_ok=True)

# --- Pli : souplesse S et rigidité réduite Q ---
Q = lam.ply_stiffness(lam.ply_compliance(config.E1, config.E2, config.NU12, config.G12))

# --- Algorithme génétique ---
best_angles, best_cost, history = ga.run_ga(
    Q, config.T_PLY, config.N_PLIES, config.POP_SIZE, config.N_GENERATIONS,
    config.P_CROSSOVER, config.P_MUTATION, config.SELECTION_PRESSURE, seed)

# --- Statistiques de la population (une ligne par génération) ---
with open(os.path.join(out_dir, "ga_statistics.csv"), "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["generation", "min", "mean", "max", "std"], delimiter=";")
    writer.writeheader()
    writer.writerows(history)

# --- Figures ---
A_star, B_star, D_star, _ = lam.laminate_matrices(Q, best_angles, config.T_PLY)
plots.plot_convergence(history, out_dir)
plots.plot_polar_diagrams(Q, A_star, B_star, D_star, out_dir)

print(f"Meilleur coût Phi : {best_cost:.6e}")
print("Meilleur empilement : [" + "/".join(str(int(a)) for a in best_angles) + "]")
print(f"Résultats dans {out_dir}")
