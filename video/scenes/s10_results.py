"""
Scene 10 - Results (scenario.md, about 1:05).

Convergence curves and the population cloud from build/data/ga_population.npz
(written by record_population.py, seed 1), the best stacking, its arrows for
R0(A*) and R1(D*), and the polar diagrams Q -> A* -> D*, B* on its own scale.
All mechanical values are recomputed with the project code.
"""

from manim import (
    Axes, Create, DashedLine, Dot, FadeIn, FadeOut, LaggedStart, Transform,
    ValueTracker, VGroup, VMobject, Write, always_redraw, Circle, GrowArrow, Arrow,
    SurroundingRectangle, Integer,
)

from common import (
    ACCENT, BUILD_DIR, COL_A, COL_B, COL_D, COL_Q, DOWN, FG, LEFT, MUTED, RIGHT, UP,
    NarratedScene, arrow_chain, config, l1111, math, np, polar_curve, tex,
)

import laminate as lam  # project code, read-only
import polar as pol

DATA = np.load(BUILD_DIR / "data" / "ga_population.npz")
COSTS = DATA["costs"]                      # (n_gen, N)
BEST = DATA["final_best"].astype(int)
Q = lam.ply_stiffness(lam.ply_compliance(config.E1, config.E2, config.NU12, config.G12))
A_S, B_S, D_S, _ = lam.laminate_matrices(Q, BEST, config.T_PLY)
PP = {k: pol.polar_parameters(m) for k, m in (("Q", Q), ("A", A_S), ("B", B_S), ("D", D_S))}


def fr(x, digits=0):
    """French number formatting: 17693.4 -> '17\\,693'."""
    s = f"{x:,.{digits}f}".replace(",", " ").replace(".", "{,}")
    return s.replace(" ", r"\,")


class S10Results(NarratedScene):
    def construct(self):
        n_gen = COSTS.shape[0]
        lo, hi = -5.0, 0.0                        # log10 range of the cost axis
        conv = Axes(x_range=[0, n_gen, 100], y_range=[lo, hi, 1], x_length=6.0, y_length=4.4,
                    tips=False, axis_config={"color": MUTED, "stroke_width": 2, "font_size": 22},
                    y_axis_config={"include_numbers": False}, x_axis_config={"include_numbers": True}
                    ).move_to([-3.3, -0.2, 0])
        conv.x_axis.shift(conv.c2p(0, lo) - conv.c2p(0, 0))     # x axis at the bottom
        ylabels = VGroup(*[math(rf"10^{{{k}}}", 22, MUTED).next_to(conv.c2p(0, k), LEFT, buff=0.15)
                           for k in range(int(lo), int(hi) + 1)])
        conv_t = tex(r"coût $\Phi$ (échelle log) par génération", 26, FG).next_to(conv, UP, buff=0.3)
        xl = tex("génération", 22, MUTED).next_to(conv, DOWN, buff=0.45)
        head = tex(r"Calcul complet, graine 1 (environ 35 s)", 38, ACCENT).to_edge(UP, buff=0.3)

        with self.voice("Voici un calcul complet, avec la graine 1. Il tourne en 35 secondes environ."):
            self.play(FadeIn(head), Create(conv), FadeIn(ylabels), FadeIn(conv_t), FadeIn(xl), run_time=1.4)

        gen = ValueTracker(0)

        def curve(stat, color, width):
            def build():
                g = max(int(gen.get_value()), 1)
                vals = np.log10(np.clip(stat[:g + 1], 10**lo, 10**hi))
                pts = [conv.c2p(i, v) for i, v in enumerate(vals)]
                m = VMobject(color=color, stroke_width=width)
                if len(pts) > 1:
                    m.set_points_as_corners(pts)
                return m
            return always_redraw(build)

        c_min = curve(COSTS.min(1), ACCENT, 4)
        c_mean = curve(COSTS.mean(1), COL_Q, 2.5)
        c_max = curve(COSTS.max(1), COL_D, 1.5)
        legend = VGroup(tex("meilleur", 22, ACCENT), tex("moyenne", 22, COL_Q), tex("pire", 22, COL_D)
                        ).arrange(RIGHT, buff=0.4).next_to(conv, UP, buff=0.75)

        # Population cloud: one dot per individual, x jitter, y = log10(cost)
        cloud_ax = Axes(x_range=[0, 1, 1], y_range=[lo, hi, 1], x_length=4.2, y_length=4.4, tips=False,
                        axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": False}
                        ).move_to([3.6, -0.2, 0])
        cloud_ax.x_axis.shift(cloud_ax.c2p(0, lo) - cloud_ax.c2p(0, 0))
        jitter = np.random.default_rng(0).uniform(0.05, 0.95, COSTS.shape[1])

        def cloud():
            g = min(int(gen.get_value()), n_gen - 1)
            y = np.log10(np.clip(COSTS[g], 10**lo, 10**hi))
            return VGroup(*[Dot(cloud_ax.c2p(x, v), radius=0.025, color=COL_Q, fill_opacity=0.7)
                            for x, v in zip(jitter, y)])

        dots = always_redraw(cloud)
        cloud_t = tex(r"les 500 individus", 26, FG).next_to(cloud_ax, UP, buff=0.3)
        counter = VGroup(tex("génération", 24, MUTED), Integer(0, font_size=28, color=FG)
                         ).arrange(RIGHT, buff=0.15).next_to(cloud_ax, DOWN, buff=0.3)
        counter[1].add_updater(lambda m: m.set_value(min(int(gen.get_value()) + 1, n_gen)))

        with self.voice("Le meilleur coût descend par paliers et ne remonte jamais, grâce à "
                        "l'élitisme."):
            self.add(c_max, c_mean, c_min)
            self.play(FadeIn(legend), Create(cloud_ax), FadeIn(cloud_t), FadeIn(counter), run_time=0.6)
            self.add(dots)
            self.play(gen.animate.set_value(150), run_time=3.2, rate_func=lambda t: t)

        with self.voice("Au début, la population est très dispersée ; à la fin, elle s'est "
                        "resserrée autour des meilleures solutions."):
            self.play(gen.animate.set_value(n_gen - 1), run_time=4.0, rate_func=lambda t: t)

        # ----- best stacking -----
        stack = "/".join(f"{{{a}}}" if a < 0 else str(a) for a in BEST)
        best_t = math(rf"[{stack}]", 30, FG)
        cost = DATA["final_cost"]
        m, e = f"{float(cost):.1e}".split("e")
        best_c = math(rf"\Phi = {m.replace('.', '{,}')} \times 10^{{{int(e)}}}", 40, ACCENT)
        best = VGroup(tex("meilleur empilement (pli 1 en bas) :", 28, MUTED), best_t, best_c
                      ).arrange(DOWN, buff=0.3).to_edge(UP, buff=0.5)

        with self.voice("Le meilleur stratifié a un coût de 4 fois 10 puissance moins 5."):
            dots.clear_updaters()
            counter[1].clear_updaters()
            self.play(FadeOut(VGroup(conv, ylabels, conv_t, xl, head, legend, cloud_ax, cloud_t,
                                     counter, dots, c_min, c_mean, c_max)), run_time=0.8)
            self.play(FadeIn(best), run_time=1.2)

        # ----- arrows of the best stacking -----
        n = len(BEST)
        z = np.arange(n + 1) - n / 2
        d_w = 4 * (z[1:]**3 - z[:-1]**3)
        cA = np.array([-3.4, -1.6, 0])
        cD = np.array([3.4, -1.6, 0])
        arA, endA = arrow_chain(np.radians(4 * BEST), None, origin=cA, scale=0.75, colors=[COL_A], stroke=3)
        arD, endD = arrow_chain(np.radians(2 * BEST), d_w / d_w.mean(), origin=cD, scale=0.75,
                                colors=[COL_D], stroke=3)
        arA.shift(cA - arA.get_center())

        def ends(chain):
            """Start (white) and end (yellow) of an arrow chain: almost the same point."""
            g = VGroup(Dot(chain[0].get_start(), radius=0.07, color=FG),
                       Dot(chain[-1].get_end(), radius=0.05, color=ACCENT))
            return g

        arD.shift(cD - arD.get_center())
        eA, eD = ends(arA), ends(arD)
        labA = tex(rf"$R_0^{{A^*}} = {fr(PP['A']['R0'], 1)}$ MPa (pli seul : {fr(PP['Q']['R0'])} MPa)",
                   28, COL_A).next_to(cA + DOWN * 1.5, DOWN, buff=0.1)
        labD = tex(rf"$R_1^{{D^*}} = {fr(PP['D']['R1'], 1)}$ MPa (pli seul : {fr(PP['Q']['R1'])} MPa)",
                   28, COL_D).next_to(cD + DOWN * 1.5, DOWN, buff=0.1)

        with self.voice("R0 de A étoile vaut 44 MPa, contre 17 700 pour le pli seul : 400 fois "
                        "moins."):
            self.play(LaggedStart(*[GrowArrow(a) for a in arA], lag_ratio=0.15), run_time=2.4)
            self.play(FadeIn(labA), FadeIn(eA), run_time=0.6)

        with self.voice("R1 de D étoile vaut 59 MPa au lieu de 19 000."):
            self.play(LaggedStart(*[GrowArrow(a) for a in arD], lag_ratio=0.15), run_time=2.4)
            self.play(FadeIn(labD), FadeIn(eD), run_time=0.6)

        # ----- polar diagrams -----
        center = np.array([-2.6, -0.3, 0])
        scale = 2.7 / l1111(PP["Q"], 0.0)          # Q at 0 deg (161.6 GPa) -> 2.7 units
        rings = VGroup(*[Circle(radius=r, color=MUTED, stroke_width=1, stroke_opacity=0.35).move_to(center)
                         for r in (0.675, 1.35, 2.025, 2.7)])
        ring_lab = tex(r"anneaux : 40, 80, 120, 160 GPa", 22, MUTED).next_to(rings, DOWN, buff=0.15)
        diag = polar_curve(PP["Q"], center, scale, COL_Q, stroke=5)
        dlab = tex(r"pli seul : « 8 » allongé dans le sens des fibres", 30, COL_Q).move_to([3.4, 1.2, 0])

        with self.voice("Sur les diagrammes polaires, le pli seul fait un huit allongé dans le "
                        "sens des fibres."):
            self.play(FadeOut(VGroup(best, arA, arD, labA, labD, eA, eD)), run_time=0.6)
            self.play(FadeIn(rings), FadeIn(ring_lab), Create(diag), FadeIn(dlab), run_time=1.6)

        def morph(key, color, label, text):
            new = polar_curve(PP[key], center, scale, color, stroke=5)
            new_lab = tex(label, 30, color).move_to(dlab)
            with self.voice(text):
                self.play(Transform(diag, new), Transform(dlab, new_lab), run_time=1.8)

        morph("A", COL_A, r"$\mathbf{A}^*$ : deux lobes, orthotropie $R_0$",
              "A étoile n'a plus que ses deux lobes : c'est l'orthotropie R0.")
        morph("D", COL_D, r"$\mathbf{D}^*$ : presque rond, 4 bosses légères",
              "D étoile est presque rond, avec quatre bosses très légères.")

        # B* on its own scale (MPa), in a small inset
        bc = np.array([3.6, -1.4, 0])
        b_vals = np.abs(np.array([pol.stiffness_from_polar(PP["B"], t)[0, 0]
                                  for t in np.linspace(0, 2 * np.pi, 361)]))
        b_scale = 1.4 / b_vals.max()
        b_curve = polar_curve(PP["B"], bc, b_scale, COL_B, stroke=4)
        b_ring = Circle(radius=1.4, color=MUTED, stroke_width=1, stroke_opacity=0.5).move_to(bc)
        b_lab = tex(rf"$\mathbf{{B}}^*$, échelle à part : max {fr(b_vals.max())} MPa", 26, COL_B
                    ).next_to(b_ring, DOWN, buff=0.15)
        a_max = np.max(np.abs([pol.stiffness_from_polar(PP["A"], t)[0, 0]
                               for t in np.linspace(0, 2 * np.pi, 361)]))
        a_lab = tex(rf"(pour $\mathbf{{A}}^*$ : max {fr(a_max / 1000)} GPa)", 24, MUTED
                    ).next_to(b_lab, DOWN, buff=0.1)

        with self.voice("Et B étoile est si petit qu'il lui faut sa propre échelle, quelques "
                        "centaines de MPa contre près de 85 000 pour A étoile."):
            self.play(Create(b_ring), Create(b_curve), FadeIn(b_lab), FadeIn(a_lab), run_time=1.8)

        close = tex(r"angles entiers : pas pile zéro, mais très près", 32, ACCENT).to_edge(UP, buff=0.5)
        with self.voice("Avec des angles entiers, on ne tombe pas pile sur zéro, mais on en est "
                        "très près."):
            self.play(FadeIn(close, shift=0.2 * DOWN), run_time=0.8)
