"""
Figures du rapport (énoncé 3.1.c), enregistrées en PNG :
- convergence.png    : meilleur, moyen et pire coût, et écart-type, par génération
- polar_diagrams.png : diagrammes polaires de L11(theta) pour Q, A*, B*, D*
"""

import os

import matplotlib
matplotlib.use("Agg")           # dessine dans des fichiers, sans ouvrir de fenêtre
import matplotlib.pyplot as plt
import numpy as np

import polar as pol


def plot_convergence(history, out_dir):
    """Évolution du coût et de sa dispersion au fil des générations."""
    gens = [h["generation"] for h in history]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

    # En haut : coûts sur un axe log (ils baissent de plusieurs ordres de grandeur)
    ax1.semilogy(gens, [h["min"] for h in history], label="Meilleur", linewidth=2.0)
    ax1.semilogy(gens, [h["mean"] for h in history], "--", label="Moyenne")
    ax1.semilogy(gens, [h["max"] for h in history], ":", label="Pire")
    ax1.set_ylabel(r"Fonction de coût $\Phi$")
    ax1.set_title("Convergence de l'algorithme génétique")
    ax1.grid(True, which="both", linestyle=":")
    ax1.legend()

    # En bas : écart-type = diversité de la population
    ax2.plot(gens, [h["std"] for h in history], color="green")
    ax2.set_xlabel("Génération")
    ax2.set_ylabel(r"Écart-type de $\Phi$")
    ax2.grid(True, linestyle=":")

    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "convergence.png"), dpi=300)
    plt.close(fig)


def plot_polar_diagrams(Q, A_star, B_star, D_star, out_dir):
    """
    Diagrammes polaires de |L11(theta)| (P2 slide 52). Cibles du groupe 1 :
    A* en « cacahuète » (R0 = 0), B* nul, D* en carré arrondi (R1 = 0).
    """
    thetas = np.linspace(0.0, 2.0 * np.pi, 361)
    panels = [("Pli Q", Q, 1000.0, "GPa"), ("Membrane A*", A_star, 1000.0, "GPa"),
              ("Couplage B*", B_star, 1.0, "MPa"), ("Flexion D*", D_star, 1000.0, "GPa")]

    fig, axes = plt.subplots(1, 4, figsize=(18, 4.8), subplot_kw={"projection": "polar"})
    for ax, (title, L, scale, unit) in zip(axes, panels):
        values = pol.component_11(pol.polar_parameters(L), thetas) / scale
        # Un rayon ne peut pas être négatif (B*11 peut l'être) : valeur absolue
        ax.plot(thetas, np.abs(values), linewidth=2.0)
        ax.set_title(f"{title} ({unit})", pad=14, fontweight="bold")

    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "polar_diagrams.png"), dpi=300)
    plt.close(fig)
