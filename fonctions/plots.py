"""
===============================================================================
FIGURES (EVCSP - M. Montemurro)
===============================================================================
Produit les figures demandées par l'énoncé (section 3.1.c) :
1. convergence    : coût du meilleur individu, coût moyen et coût du pire
                    à chaque génération, et dispersion (écart-type) de la
                    population.
2. polar_diagrams : diagrammes polaires de la première composante
                    L_1111(theta) du pli Q, de la membrane A*, du couplage B*
                    et de la flexion D* (comme sur la slide 52 de P2).

Chaque figure est enregistrée trois fois : SVG et PDF (formats vectoriels,
pour le rapport) et PNG (300 dpi, pour un aperçu rapide).
Seuls NumPy et Matplotlib sont utilisés.
===============================================================================
"""

import os

import matplotlib
matplotlib.use("Agg")           # dessine dans des fichiers, sans ouvrir de fenêtre
import matplotlib.pyplot as plt
import numpy as np

import polar as pol


# =============================================================================
# 0. ENREGISTREMENT
# =============================================================================
def _save(fig, out_dir, name):
    """
    Enregistre la figure en name.svg, name.pdf et name.png dans out_dir, la
    ferme (pour libérer la mémoire) et renvoie la liste des fichiers écrits.
    """
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for ext in ("svg", "pdf", "png"):
        path = os.path.join(out_dir, f"{name}.{ext}")
        # dpi ne compte que pour le PNG ; SVG et PDF restent vectoriels
        fig.savefig(path, dpi=300, bbox_inches="tight")
        paths.append(path)
    plt.close(fig)
    return paths


# =============================================================================
# 1. COURBE DE CONVERGENCE ET STATISTIQUES DE LA POPULATION
# =============================================================================
def plot_convergence(history, out_dir):
    """
    history : liste de dictionnaires renvoyée par ga.run_ga, un par
              génération, avec les clés "generation", "min", "mean", "max", "std".
    """
    # Un tableau NumPy par statistique, facile à tracer
    gens = np.array([h["generation"] for h in history])
    c_min = np.array([h["min"] for h in history])
    c_mean = np.array([h["mean"] for h in history])
    c_max = np.array([h["max"] for h in history])
    c_std = np.array([h["std"] for h in history])

    # Deux graphes l'un sous l'autre, avec le même axe des générations
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

    # --- En haut : meilleur, moyen et pire coût ---
    # Axe y logarithmique : le coût baisse de plusieurs ordres de grandeur,
    # un axe linéaire écraserait la fin de la convergence sur 0.
    ax1.semilogy(gens, c_min, label=r"Meilleur ($\Phi_{\min}$)", color="#1f77b4", linewidth=2.0)
    ax1.semilogy(gens, c_mean, label=r"Moyenne ($\Phi_{\mathrm{moy}}$)", color="#ff7f0e",
                 linestyle="--", linewidth=1.5)
    ax1.semilogy(gens, c_max, label=r"Pire ($\Phi_{\max}$)", color="#7f7f7f",
                 linestyle=":", linewidth=1.2)
    ax1.set_ylabel(r"Fonction de coût $\Phi$ (échelle log)")
    ax1.set_title("Convergence de l'algorithme génétique")
    ax1.grid(True, which="both", linestyle=":", alpha=0.6)
    ax1.legend(loc="upper right")

    # --- En bas : dispersion de la population ---
    # Un grand écart-type = population variée ; un petit = tous les individus
    # se sont regroupés dans la même zone.
    ax2.plot(gens, c_std, label=r"Écart-type ($\sigma_\Phi$)", color="#2ca02c", linewidth=1.5)
    ax2.set_xlabel("Génération")
    ax2.set_ylabel(r"Écart-type de $\Phi$")
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend(loc="upper right")

    plt.tight_layout()
    return _save(fig, out_dir, "convergence")


# =============================================================================
# 2. DIAGRAMMES POLAIRES DES MATRICES DE RIGIDITÉ (P2 slides 37-38 et 52)
# =============================================================================
def _component_1111(L, thetas_rad):
    """
    Première composante L_1111(theta) [MPa] du tenseur L dans un repère tourné
    de theta. Avec la méthode polaire, tourner le repère revient simplement à
    retrancher theta à Phi0 et Phi1 (P2 slide 37) : c'est ce que fait
    pol.stiffness_from_polar, dont la case [0, 0] est L_1111(theta).
    """
    pp = pol.polar_parameters(L)
    vals = np.array([pol.stiffness_from_polar(pp, t)[0, 0] for t in thetas_rad])
    return vals, pp


def plot_polar_diagrams(Q, A_star, B_star, D_star, out_dir):
    """
    Quatre diagrammes polaires côte à côte :
    - Q  : le pli (référence, orthotropie ordinaire)
    - A* : membrane, cible du groupe 1 : R0 = 0 (orthotropie R0)
    - B* : couplage, cible du groupe 1 : B* = 0 (la courbe se resserre au centre)
    - D* : flexion, cible du groupe 1 : R1 = 0 (symétrie du carré)
    B* a sa propre échelle radiale, sinon il serait invisible.
    """
    # Tour complet au pas de 1°, pour que chaque courbe soit fermée
    thetas = np.linspace(0.0, 2.0 * np.pi, 361)

    q_vals, _ = _component_1111(Q, thetas)
    a_vals, pp_A = _component_1111(A_star, thetas)
    b_vals, pp_B = _component_1111(B_star, thetas)
    d_vals, pp_D = _component_1111(D_star, thetas)

    fig, axes = plt.subplots(1, 4, figsize=(18, 4.8), subplot_kw={"projection": "polar"})

    # (axe, valeurs, unité, couleur, titre). Q, A*, D* en GPa ; B* en MPa car
    # il est plusieurs ordres de grandeur plus petit.
    panels = [
        (axes[0], q_vals / 1000.0, "GPa", "#1f77b4", "Pli $Q$\n(orthotropie ordinaire)"),
        (axes[1], a_vals / 1000.0, "GPa", "#2ca02c",
         f"Membrane $A^*$\n(orthotropie $R_0$, $R_0$ = {pp_A['R0']:.1f} MPa)"),
        (axes[2], b_vals, "MPa", "#9467bd",
         f"Couplage $B^*$\n(cible 0, $R_0$ = {pp_B['R0']:.2f}, $R_1$ = {pp_B['R1']:.2f} MPa)"),
        (axes[3], d_vals / 1000.0, "GPa", "#d62728",
         f"Flexion $D^*$\n(symétrie du carré, $R_1$ = {pp_D['R1']:.1f} MPa)"),
    ]

    for ax, vals, unit, color, title in panels:
        # Un diagramme polaire ne peut pas afficher de rayon négatif (B*_11
        # peut être négatif) : on trace la valeur absolue et on l'indique.
        ax.plot(thetas, np.abs(vals), color=color, linewidth=2.0)
        ax.set_title(title, pad=14, fontweight="bold")
        ax.set_xlabel(f"|L_1111| ({unit})")
        ax.grid(True, linestyle=":", alpha=0.7)

    plt.tight_layout()
    return _save(fig, out_dir, "polar_diagrams")
