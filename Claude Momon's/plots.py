"""
===============================================================================
GÉNÉRATION DES GRAPHIQUES (EVCSP - M. Montemurro)
===============================================================================
Ce module produit les deux figures demandées dans l'énoncé (section 3.1.c)
au format PNG (300 dpi) :
1. convergence.png    : évolution de la fonction de coût (min, moyenne, max)
                        et de sa dispersion (écart-type) au fil des générations.
2. polar_diagrams.png : diagrammes polaires de la rigidité directionnelle
                        L_1111(theta) pour le pli de base Q, la membrane A*
                        et la flexion D*.

Bibliothèques externes autorisées ici : NumPy et Matplotlib (pour les tracés).
===============================================================================
"""

import os
import numpy as np
import matplotlib.pyplot as plt

import polar as pol  # Module interne pour le calcul des paramètres polaires


# =============================================================================
# 1. COURBES DE CONVERGENCE ET STATISTIQUES DE LA POPULATION
# =============================================================================
def plot_convergence(history, out_dir):
    """
    Trace l'évolution des statistiques de la fonction de coût Phi(delta)
    au fil des générations et sauvegarde 'convergence.png' dans out_dir.

    Paramètres
    ----------
    history : list[dict]
        Liste renvoyée par ga.run_ga(...). Chaque dictionnaire correspond à une
        génération et contient les clés : "generation", "min", "mean", "max", "std".
    out_dir : str
        Chemin du dossier de sortie où enregistrer l'image (ex: "results").

    Retourne
    --------
    out_path : str
        Chemin complet du fichier PNG généré.
    """
    # Crée le dossier de sortie s'il n'existe pas encore (sans erreur s'il existe déjà)
    os.makedirs(out_dir, exist_ok=True)

    # On extrait chaque série de valeurs depuis la liste de dictionnaires
    # pour obtenir des tableaux NumPy 1D faciles à tracer.
    gens = np.array([h["generation"] for h in history])
    c_min = np.array([h["min"] for h in history])
    c_mean = np.array([h["mean"] for h in history])
    c_max = np.array([h["max"] for h in history])
    c_std = np.array([h["std"] for h in history])

    # Création d'une figure contenant 2 sous-graphes empilés verticalement (2 lignes, 1 colonne).
    # sharex=True : les deux graphes partagent exactement le même axe horizontal (Génération).
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

    # --- Sous-graphe 1 (haut) : Évolution du meilleur individu, moyenne et pire ---
    # On utilise ax1.semilogy(...) (axe Y en échelle logarithmique) car la fonction
    # de coût Phi décroît sur plusieurs ordres de grandeur (de ~10^-1 à ~10^-5).
    # En échelle linéaire, la fin de la convergence serait écrasée sur l'axe 0.
    ax1.semilogy(gens, c_min, label=r"Meilleur ($\Phi_{\min}$)", color="#1f77b4", linewidth=2.0)
    ax1.semilogy(gens, c_mean, label=r"Moyenne ($\Phi_{\mathrm{moy}}$)", color="#ff7f0e", linestyle="--", linewidth=1.5)
    ax1.semilogy(gens, c_max, label=r"Pire ($\Phi_{\max}$)", color="#7f7f7f", linestyle=":", linewidth=1.2)

    ax1.set_ylabel(r"Fonction de coût $\Phi$ (échelle log)")
    ax1.set_title("Convergence de l'algorithme génétique")
    # Grille sur les graduations majeures et mineures pour lire facilement les puissances de 10
    ax1.grid(True, which="both", linestyle=":", alpha=0.6)
    ax1.legend(loc="upper right")

    # --- Sous-graphe 2 (bas) : Dispersion statistique de la population ---
    # L'écart-type (std) mesure si les individus de la population sont encore
    # variés (std élevé) ou s'ils ont tous convergé vers la même zone (std faible).
    ax2.plot(gens, c_std, label=r"Écart-type ($\sigma_\Phi$)", color="#2ca02c", linewidth=1.5)
    ax2.set_xlabel("Génération")
    ax2.set_ylabel(r"Écart-type de $\Phi$")
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend(loc="upper right")

    # Ajuste automatiquement les espacements pour éviter que les titres/labels ne se chevauchent
    plt.tight_layout()

    # Sauvegarde en PNG haute résolution (300 dpi) puis fermeture pour libérer la RAM
    out_path = os.path.join(out_dir, "convergence.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path


# =============================================================================
# 2. DIAGRAMMES POLAIRES DES MATRICES DE RIGIDITÉ (P2 slide 38)
# =============================================================================
def _directional_stiffness_1111(L, thetas_rad):
    """
    Calcule la composante de rigidité longitudinale L_1111(theta) [MPa] pour
    tout angle theta dans [0, 2*pi] en utilisant le formalisme polaire.

    Rappel cours (P2 slide 37) :
    Une rotation du repère d'un angle theta consiste simplement à soustraire
    theta aux deux angles polaires Phi0 et Phi1. C'est ce que fait
    pol.stiffness_from_polar(pp, t), dont le terme [0, 0] est L_1111(theta).
    """
    # Extraction des 6 paramètres polaires (T0, T1, R0, R1, Phi0, Phi1) de la matrice L
    pp = pol.polar_parameters(L)

    # Évaluation de L_1111(theta) pour chaque angle du cercle complet
    vals = np.array([pol.stiffness_from_polar(pp, t)[0, 0] for t in thetas_rad])
    return vals, pp


def plot_polar_diagrams(Q, A_star, D_star, out_dir):
    """
    Trace côte à côte les diagrammes polaires de :
    - Q      : pli élémentaire (référence orthotrope standard)
    - A_star : rigidité de membrane homogénéisée (cible Groupe 1 : orthotropie-R0, R0 = 0)
    - D_star : rigidité de flexion homogénéisée (cible Groupe 1 : symétrie du carré, R1 = 0)

    Sauvegarde l'image 'polar_diagrams.png' dans out_dir.
    """
    os.makedirs(out_dir, exist_ok=True)

    # On discrétise le cercle complet [0, 2*pi] en 361 points (de 0° à 360° par pas de 1°)
    # afin que la courbe polaire soit parfaitement fermée et lisse.
    thetas = np.linspace(0.0, 2.0 * np.pi, 361)

    # Calcul des courbes directionnelles L_1111(theta) et récupération des paramètres polaires
    q_vals, _ = _directional_stiffness_1111(Q, thetas)
    a_vals, pp_A = _directional_stiffness_1111(A_star, thetas)
    d_vals, pp_D = _directional_stiffness_1111(D_star, thetas)

    # Création d'une figure à 3 sous-graphes en coordonnées polaires (1 ligne, 3 colonnes)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8), subplot_kw={"projection": "polar"})

    # Configuration de chaque panneau : (axe, valeurs en GPa, couleur, titre)
    # On divise par 1000.0 pour afficher des GPa au lieu des MPa (plus lisible).
    panels = [
        (
            axes[0],
            q_vals / 1000.0,
            "#1f77b4",
            "Pli de base $Q$\n(orthotropie standard)",
        ),
        (
            axes[1],
            a_vals / 1000.0,
            "#2ca02c",
            f"Membrane $A^*$\n(orthotropie-$R_0$, $R_0 = {pp_A['R0']:.1f}$ MPa)",
        ),
        (
            axes[2],
            d_vals / 1000.0,
            "#d62728",
            f"Flexion $D^*$\n(symétrie du carré, $R_1 = {pp_D['R1']:.1f}$ MPa)",
        ),
    ]

    # Boucle de tracé uniforme sur les 3 panneaux polaires
    for ax, vals_gpa, color, title in panels:
        ax.plot(thetas, vals_gpa, color=color, linewidth=2.0)
        # pad=14 décale légèrement le titre vers le haut pour qu'il ne touche pas "90°"
        ax.set_title(title, pad=14, fontweight="bold")
        ax.grid(True, linestyle=":", alpha=0.7)

    # Étiquette d'unité sur le premier graphe (labelpad=28 pour éviter le chevauchement)
    axes[0].set_ylabel(r"$L_{1111}$ (GPa)", labelpad=28)

    plt.tight_layout()

    # Sauvegarde en PNG haute résolution (300 dpi) puis fermeture
    out_path = os.path.join(out_dir, "polar_diagrams.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path
