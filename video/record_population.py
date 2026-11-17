"""
Re-run the group 1 GA and record the WHOLE population at every generation,
for the convergence animation of scene 10.

The loop below is a copy of ga.run_ga (Claude Momon's/ga.py) that only adds
the recording; it calls the project's own operators, which are not modified.
With the same seed it must find the same best stacking as main.py: this is
checked at the end.

Usage (from the video/ folder):
    ../.venv/Scripts/python record_population.py
Output: build/data/ga_population.npz
    costs        (n_generations, N)  cost of every individual
    best_angles  (n_generations, 20) best stacking of each generation
    final_best   (20,)               best stacking at the end
"""

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "Claude Momon's"))

import config  # noqa: E402
import fitness as fit  # noqa: E402
import ga  # noqa: E402
import laminate as lam  # noqa: E402

OUT = HERE / "build" / "data" / "ga_population.npz"
EXPECTED_BEST = [22, -41, 80, -15, -89, 42, -61, 61, -74, 83,
                 -72, -38, 67, -52, 43, 84, 5, 38, -25, -82]   # results/best_laminate.txt


def main():
    Q = lam.ply_stiffness(lam.ply_compliance(config.E1, config.E2, config.NU12, config.G12))
    n, N = config.N_PLIES, config.POP_SIZE
    args = (Q, config.T_PLY, config.OBJECTIVES, config.K_A, config.K_D)
    rng = np.random.default_rng(config.SEED)

    # Same sequence of calls (and so of random draws) as ga.run_ga
    pop_bits = ga.init_population(N, n, rng)
    angles = ga.decode_population(pop_bits, n)
    costs = ga.evaluate_population(angles, *args)

    all_costs, best_angles = [], []
    for gen in range(config.N_GENERATIONS):
        best_idx = int(np.argmin(costs))
        best_bits = pop_bits[best_idx].copy()
        best_cost = float(costs[best_idx])
        all_costs.append(costs.copy())
        best_angles.append(angles[best_idx].copy())
        if gen % 50 == 0:
            print(f"gen {gen:3d}  best {best_cost:.4e}")

        fit_vals = fit.fitness(costs, p=config.SELECTION_PRESSURE)
        parents = ga.roulette_selection(pop_bits, fit_vals, rng)
        offspring = ga.crossover_population(parents, config.P_CROSSOVER, rng, "one_point")
        offspring = ga.mutate_population(offspring, config.P_MUTATION, n, rng)
        offspring, _ = ga.reject_invalid_genes(offspring, parents, n)
        offspring_angles = ga.decode_population(offspring, n)
        offspring_costs = ga.evaluate_population(offspring_angles, *args)

        worst_idx = int(np.argmax(offspring_costs))
        offspring[worst_idx] = best_bits
        offspring_costs[worst_idx] = best_cost

        pop_bits, costs = offspring, offspring_costs
        angles = ga.decode_population(pop_bits, n)

    final_best = angles[int(np.argmin(costs))]
    assert list(final_best) == EXPECTED_BEST, f"different best stacking: {final_best}"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, costs=np.array(all_costs), best_angles=np.array(best_angles),
                        final_best=final_best, final_cost=float(costs.min()))
    print(f"best {final_best.tolist()}  cost {costs.min():.4e}  -> {OUT}")


if __name__ == "__main__":
    main()
