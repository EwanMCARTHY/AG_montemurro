"""
===============================================================================
FIGURES (EVCSP - M. Montemurro)
===============================================================================
Produces the figures asked by the statement (section 3.1.c):
1. convergence    : best / mean / worst cost per generation, and the spread
                    (standard deviation) of the population.
2. polar_diagrams : polar diagrams of the first component L_1111(theta) of
                    the ply Q, of the membrane A*, coupling B* and bending D*
                    stiffness (as on P2 slide 52).

Each figure is saved three times: SVG and PDF (vector formats, for the
report) and PNG (300 dpi, for a quick look).
Only NumPy and Matplotlib are used.
===============================================================================
"""

import os

import matplotlib
matplotlib.use("Agg")           # draw into files, no window needed
import matplotlib.pyplot as plt
import numpy as np

import polar as pol


# =============================================================================
# 0. SAVING HELPER
# =============================================================================
def _save(fig, out_dir, name):
    """
    Saves the figure as name.svg, name.pdf and name.png in out_dir, closes it
    (to free memory) and returns the list of written paths.
    """
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for ext in ("svg", "pdf", "png"):
        path = os.path.join(out_dir, f"{name}.{ext}")
        # dpi only matters for the PNG; SVG and PDF stay vector graphics
        fig.savefig(path, dpi=300, bbox_inches="tight")
        paths.append(path)
    plt.close(fig)
    return paths


# =============================================================================
# 1. CONVERGENCE CURVE AND POPULATION STATISTICS
# =============================================================================
def plot_convergence(history, out_dir):
    """
    history : list of dicts returned by ga.run_ga, one per generation, with
              the keys "generation", "min", "mean", "max", "std".
    """
    # One NumPy array per statistic, easy to plot
    gens = np.array([h["generation"] for h in history])
    c_min = np.array([h["min"] for h in history])
    c_mean = np.array([h["mean"] for h in history])
    c_max = np.array([h["max"] for h in history])
    c_std = np.array([h["std"] for h in history])

    # Two plots stacked vertically, sharing the generation axis
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

    # --- Top: best, mean and worst cost ---
    # Logarithmic y axis: the cost drops by several orders of magnitude, a
    # linear axis would squash the end of the convergence onto 0.
    ax1.semilogy(gens, c_min, label=r"Best ($\Phi_{\min}$)", color="#1f77b4", linewidth=2.0)
    ax1.semilogy(gens, c_mean, label=r"Mean ($\Phi_{\mathrm{mean}}$)", color="#ff7f0e",
                 linestyle="--", linewidth=1.5)
    ax1.semilogy(gens, c_max, label=r"Worst ($\Phi_{\max}$)", color="#7f7f7f",
                 linestyle=":", linewidth=1.2)
    ax1.set_ylabel(r"Cost function $\Phi$ (log scale)")
    ax1.set_title("Convergence of the genetic algorithm")
    ax1.grid(True, which="both", linestyle=":", alpha=0.6)
    ax1.legend(loc="upper right")

    # --- Bottom: spread of the population ---
    # A large standard deviation means a varied population; a small one
    # means that all individuals gathered in the same region.
    ax2.plot(gens, c_std, label=r"Standard deviation ($\sigma_\Phi$)", color="#2ca02c",
             linewidth=1.5)
    ax2.set_xlabel("Generation")
    ax2.set_ylabel(r"Standard deviation of $\Phi$")
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend(loc="upper right")

    plt.tight_layout()
    return _save(fig, out_dir, "convergence")


# =============================================================================
# 2. POLAR DIAGRAMS OF THE STIFFNESS MATRICES (P2 slides 37-38 and 52)
# =============================================================================
def _component_1111(L, thetas_rad):
    """
    First component L_1111(theta) [MPa] of the tensor L in a frame rotated by
    theta. With the polar method a rotation of the frame simply subtracts
    theta from Phi0 and Phi1 (P2 slide 37); pol.stiffness_from_polar does
    that, and its term [0, 0] is L_1111(theta).
    """
    pp = pol.polar_parameters(L)
    vals = np.array([pol.stiffness_from_polar(pp, t)[0, 0] for t in thetas_rad])
    return vals, pp


def plot_polar_diagrams(Q, A_star, B_star, D_star, out_dir):
    """
    Four polar diagrams side by side:
    - Q  : the ply (reference, ordinary orthotropy)
    - A* : membrane, group 1 target R0 = 0 (R0-orthotropy)
    - B* : coupling, group 1 target B* = 0 (curve shrinks to the centre)
    - D* : bending, group 1 target R1 = 0 (square symmetry)
    B* has its own radial scale, otherwise it would be invisible.
    """
    # Full circle, 1 deg step, so that each curve is closed
    thetas = np.linspace(0.0, 2.0 * np.pi, 361)

    q_vals, _ = _component_1111(Q, thetas)
    a_vals, pp_A = _component_1111(A_star, thetas)
    b_vals, pp_B = _component_1111(B_star, thetas)
    d_vals, pp_D = _component_1111(D_star, thetas)

    fig, axes = plt.subplots(1, 4, figsize=(18, 4.8), subplot_kw={"projection": "polar"})

    # (axis, values, unit label, colour, title). Q, A*, D* in GPa; B* in MPa
    # because it is several orders of magnitude smaller.
    panels = [
        (axes[0], q_vals / 1000.0, "GPa", "#1f77b4", "Ply $Q$\n(ordinary orthotropy)"),
        (axes[1], a_vals / 1000.0, "GPa", "#2ca02c",
         f"Membrane $A^*$\n($R_0$-orthotropy, $R_0$ = {pp_A['R0']:.1f} MPa)"),
        (axes[2], b_vals, "MPa", "#9467bd",
         f"Coupling $B^*$\n(target 0, $R_0$ = {pp_B['R0']:.2f}, $R_1$ = {pp_B['R1']:.2f} MPa)"),
        (axes[3], d_vals / 1000.0, "GPa", "#d62728",
         f"Bending $D^*$\n(square symmetry, $R_1$ = {pp_D['R1']:.1f} MPa)"),
    ]

    for ax, vals, unit, color, title in panels:
        # A polar plot cannot show negative radii (B*_11 can be negative):
        # we plot the absolute value and say so in the label.
        ax.plot(thetas, np.abs(vals), color=color, linewidth=2.0)
        ax.set_title(title, pad=14, fontweight="bold")
        ax.set_xlabel(f"|L_1111| ({unit})")
        ax.grid(True, linestyle=":", alpha=0.7)

    plt.tight_layout()
    return _save(fig, out_dir, "polar_diagrams")
