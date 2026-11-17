"""
Scene 7 - Objectives of group 1 (scenario.md, about 0:45).

The three required properties, the partial objectives Phi1, Phi4, Phi9
(P2 slides 45-47), the cost Phi = Phi1 + Phi4 + Phi9 and a 1D cut of Phi
(computed with fitness.cost) to show how many local minima it has.
"""

from manim import (
    Axes, Create, Dot, FadeIn, FadeOut, Indicate, LaggedStart, MoveAlongPath,
    RoundedRectangle, SurroundingRectangle, VGroup, VMobject, Write,
)

from common import (
    ACCENT, COL_A, COL_B, COL_D, COL_Q, DOWN, FG, LEFT, MUTED, RIGHT, UP,
    NarratedScene, config, math, np, tex,
)

import fitness as fit  # project code, read-only
import laminate as lam

Q = lam.ply_stiffness(lam.ply_compliance(config.E1, config.E2, config.NU12, config.G12))


def cost_cut(n_points=900, seed=3):
    """
    Cost along a closed path through the space of the 20 angles: starting
    from a random stacking a, ply k turns K_k half-turns (K_k in +-1..4) while
    t goes from 0 to 1, i.e. delta(t) = a + 180 t K. Angles are real numbers
    here (only for this picture). With seed 3 this cut has 16 local minima.
    """
    rng = np.random.default_rng(seed)
    a = rng.uniform(-89, 90, config.N_PLIES)
    K = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4], config.N_PLIES)
    t = np.linspace(0, 1, n_points)
    c = np.array([fit.cost(a + ti * K * 180.0, Q, config.T_PLY, config.OBJECTIVES) for ti in t])
    return t, c


class S07Objectives(NarratedScene):
    def construct(self):
        row = tex(r"Groupe 1 (20 plis) :\\découplage, orthotropie $R_0$ en membrane, "
                  r"orthotropie $R_1$ en flexion", 30, FG).to_edge(UP, buff=0.4)

        with self.voice("Notre groupe doit obtenir trois propriétés."):
            self.play(FadeIn(row, shift=0.2 * DOWN), run_time=1.0)

        specs = [
            (r"découplage", r"\mathbf{B}^* = 0",
             r"\Phi_1 = \left(\frac{\|\mathbf{B}^*\|}{\|\mathbf{Q}\|}\right)^2", COL_B,
             "Le découplage, c'est-à-dire B étoile nul."),
            (r"orthotropie $R_0$, membrane", r"R_0^{A^*} = 0",
             r"\Phi_4 = \left(\frac{R_0^{A^*}}{R_0}\right)^2", COL_A,
             "L'orthotropie R0 en membrane : R0 de A étoile nul."),
            (r"$R_1$ nul en flexion", r"R_1^{D^*} = 0",
             r"\Phi_9 = \left(\frac{R_1^{D^*}}{R_1}\right)^2", COL_D,
             "Et en flexion, R1 de D étoile nul."),
        ]
        cards = VGroup()
        formulas = VGroup()
        for i, (name, cond, form, col, text) in enumerate(specs):
            box = RoundedRectangle(width=4.0, height=3.4, corner_radius=0.2, color=col, stroke_width=3)
            box.move_to([-4.3 + 4.3 * i, 0.4, 0])
            title = tex(name, 30, col).move_to(box.get_top() + DOWN * 0.45)
            c = math(cond, 40, FG).move_to(box.get_center() + UP * 0.35)
            f = math(form, 38, FG).move_to(box.get_center() + DOWN * 0.9)
            cards.add(VGroup(box, title, c))
            formulas.add(f)
            with self.voice(text):
                self.play(Create(box), FadeIn(title), Write(c), run_time=1.2)

        with self.voice("Chaque condition devient un objectif partiel, un nombre positif qui "
                        "vaut zéro quand la propriété est atteinte."):
            self.play(LaggedStart(*[Write(f) for f in formulas], lag_ratio=0.4), run_time=2.4)

        denoms = tex(r"divisé par une grandeur du pli $\Rightarrow$ sans unité", 30, COL_Q
                     ).next_to(cards, DOWN, buff=0.35)
        with self.voice("On divise chaque fois par une grandeur du pli, pour que les trois "
                        "soient sans unité et qu'on puisse les additionner."):
            self.play(FadeIn(denoms), *[Indicate(f, color=COL_Q, scale_factor=1.08) for f in formulas],
                      run_time=1.6)

        total = math(r"\Phi(\boldsymbol\delta) = \Phi_1 + \Phi_4 + \Phi_9, \qquad \min \Phi = 0",
                     48, ACCENT)
        total_box = SurroundingRectangle(total, color=ACCENT, buff=0.25)
        with self.voice("La fonction de coût est leur somme, et son minimum vaut zéro."):
            self.play(FadeOut(VGroup(cards, denoms, row)), formulas.animate.scale(0.8).arrange(RIGHT, buff=0.8)
                      .to_edge(UP, buff=0.6), run_time=1.0)
            self.play(Write(total), Create(total_box), run_time=1.4)

        # ----- 1D cut of the cost -----
        t, c = cost_cut()
        ax = Axes(x_range=[0, 1, 0.25], y_range=[0, float(np.ceil(c.max() * 10) / 10), 0.1],
                  x_length=10, y_length=4.2, tips=False,
                  axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": False}
                  ).move_to([0, -1.1, 0])
        pts = [ax.c2p(ti, ci) for ti, ci in zip(t, c)]
        curve = VMobject(color=ACCENT, stroke_width=3).set_points_as_corners(pts)
        xl = tex(r"une coupe à travers l'espace des 20 angles", 26, MUTED).next_to(ax, DOWN, buff=0.2)
        yl = math(r"\Phi", 34, ACCENT).next_to(ax, LEFT, buff=0.2).shift(UP * 1.6)

        with self.voice("Le piège, c'est la forme de cette fonction quand on fait varier les "
                        "angles : elle a énormément de creux locaux."):
            self.play(FadeOut(VGroup(formulas)), VGroup(total, total_box).animate.scale(0.7).to_edge(UP, buff=0.4),
                      run_time=0.8)
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.8)
            self.play(Create(curve), run_time=3.0)

        # A ball that slides down to the nearest local minimum (what a gradient
        # method would do), starting from a point on the curve.
        def descend(start):
            """Indices visited by a steepest descent along the curve."""
            path_idx = [start]
            step = -1 if c[start - 1] < c[start] else 1
            while 0 < path_idx[-1] + step < len(t) - 1 and c[path_idx[-1] + step] < c[path_idx[-1]]:
                path_idx.append(path_idx[-1] + step)
            return path_idx

        i0 = int(0.43 * len(t))
        visited = descend(i0)
        while len(visited) < 15:          # start on a slope, not at a minimum
            i0 += 7
            visited = descend(i0)
        path = VMobject().set_points_as_corners([pts[k] for k in visited])
        ball = Dot(pts[i0], radius=0.11, color=COL_Q)
        stuck = tex(r"une descente de gradient reste coincée ici", 28, COL_Q
                    ).next_to(ax, UP, buff=0.1).shift(DOWN * 0.2)
        ga = tex(r"$\Rightarrow$ l'algorithme génétique", 40, ACCENT).move_to([3.0, 1.6, 0])

        with self.voice("Une méthode de gradient s'arrêterait dans le premier venu. D'où "
                        "l'algorithme génétique."):
            self.play(FadeIn(ball), run_time=0.3)
            self.play(MoveAlongPath(ball, path), run_time=1.6)
            self.play(FadeIn(stuck), run_time=0.5)
            self.play(FadeIn(ga, shift=0.2 * UP), run_time=0.7)
