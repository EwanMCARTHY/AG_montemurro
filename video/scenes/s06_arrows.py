"""
Scene 6 - Arrows that close up (scenario.md, about 1:10).

Polar parameters of A* for identical plies (P2 slide 41), each ply as a unit
arrow e^(4i delta_k) or e^(2i delta_k) laid tip to tail, the examples
[0/45] and [0/60/-60], then the position weights b_k that reopen the sum.
"""

from manim import (
    Arrow, Circle, Create, DashedLine, Dot, FadeIn, FadeOut, GrowArrow,
    Indicate, LaggedStart, SurroundingRectangle, Transform, VGroup, Write,
    ReplacementTransform, DEGREES, Arc,
)

from common import (
    ACCENT, COL_A, COL_B, COL_D, COL_Q, DOWN, FG, LEFT, MUTED, RIGHT, UP,
    NarratedScene, arrow_chain, math, math_parts, np, tex,
)

PALETTE = [COL_Q, ACCENT, COL_A, COL_D, COL_B]


def complex_axes(center, size=2.2):
    c = np.array(center)
    return VGroup(
        DashedLine(c + LEFT * size, c + RIGHT * size, color=MUTED, stroke_width=1.5),
        DashedLine(c + DOWN * size, c + UP * size, color=MUTED, stroke_width=1.5),
    )


def chain(angles_deg, factor, center, scale, weights=None):
    """Arrow chain for sum_k w_k e^(i factor delta_k), starting at `center`."""
    arrows, end = arrow_chain(np.radians(factor * np.asarray(angles_deg, float)), weights,
                              origin=center, scale=scale, colors=PALETTE)
    return arrows, end


class S06Arrows(NarratedScene):
    def construct(self):
        iso = math(r"T_0^{A^*} = T_0,\quad T_1^{A^*} = T_1 \qquad T_0^{D^*} = T_0,\quad T_1^{D^*} = T_1",
                   40, FG).to_edge(UP, buff=0.7)
        iso_note = tex(r"les modules isotropes ne dépendent pas des angles", 30, MUTED
                       ).next_to(iso, DOWN, buff=0.3)

        with self.voice("Pour un stratifié à plis identiques, le cours donne un résultat "
                        "simple : les modules isotropes de A étoile et de D étoile sont ceux "
                        "du pli, quels que soient les angles."):
            self.play(Write(iso), run_time=2.0)
            self.play(FadeIn(iso_note), run_time=0.8)

        r0 = math_parts([r"R_0^{A^*}e^{4i\Phi_0^{A^*}} = \frac{1}{n}\,R_0e^{4i\Phi_0}",
                         r"\sum_{k=1}^{n} e^{4i\delta_k}"], 44)
        r1 = math_parts([r"R_1^{A^*}e^{2i\Phi_1^{A^*}} = \frac{1}{n}\,R_1e^{2i\Phi_1}",
                         r"\sum_{k=1}^{n} e^{2i\delta_k}"], 44)
        pair = VGroup(r0, r1).arrange(DOWN, buff=0.5).move_to([0, -0.6, 0])
        boxes = VGroup(SurroundingRectangle(r0[1], color=ACCENT, buff=0.1),
                       SurroundingRectangle(r1[1], color=ACCENT, buff=0.1))

        with self.voice("Seuls R0 et R1 dépendent de l'empilement, et ils s'écrivent comme "
                        "des sommes de nombres complexes."):
            self.play(Write(pair), run_time=2.0)
            self.play(Create(boxes), run_time=0.8)

        # ----- one ply = one unit arrow -----
        self.play(FadeOut(VGroup(iso, iso_note, boxes)), pair.animate.scale(0.62).to_edge(UP, buff=0.3),
                  run_time=0.8)
        c = np.array([-2.5, -0.7, 0])
        ax = complex_axes(c, 2.4)
        unit = Circle(radius=1.6, color=MUTED, stroke_width=1, stroke_opacity=0.5).move_to(c)
        d = 20.0
        a4 = Arrow(c, c + 1.6 * np.array([np.cos(np.radians(4 * d)), np.sin(np.radians(4 * d)), 0]),
                   buff=0, color=ACCENT, stroke_width=6)
        a2 = Arrow(c, c + 1.6 * np.array([np.cos(np.radians(2 * d)), np.sin(np.radians(2 * d)), 0]),
                   buff=0, color=COL_Q, stroke_width=6)
        arc4 = Arc(radius=0.5, angle=np.radians(4 * d), arc_center=c, color=ACCENT)
        arc2 = Arc(radius=0.8, angle=np.radians(2 * d), arc_center=c, color=COL_Q)
        lab = VGroup(
            tex(r"un pli à $\delta = 20^\circ$", 32, FG),
            tex(r"pour $R_0$ : flèche à $4\delta = 80^\circ$", 32, ACCENT),
            tex(r"pour $R_1$ : flèche à $2\delta = 40^\circ$", 32, COL_Q),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([3.2, -0.6, 0])

        with self.voice("On peut les voir comme des flèches. Chaque pli est une flèche de "
                        "longueur 1. Pour R0, elle pointe dans la direction quatre delta ; "
                        "pour R1, dans la direction deux delta."):
            self.play(FadeIn(ax), FadeIn(unit), FadeIn(lab[0]), run_time=0.8)
            self.play(GrowArrow(a4), Create(arc4), FadeIn(lab[1]), run_time=1.2)
            self.play(GrowArrow(a2), Create(arc2), FadeIn(lab[2]), run_time=1.2)

        # ----- tip to tail -----
        demo = [10, 35, -50, 70, -20]
        arrows, end = chain(demo, 4, c + LEFT * 1.0 + DOWN * 0.6, 1.0)
        total = Arrow(c + LEFT * 1.0 + DOWN * 0.6, end, buff=0, color=FG, stroke_width=4)
        rule = tex(r"bout à bout : la flèche somme donne $R$\\retour au départ $\Rightarrow R = 0$",
                   32, FG).move_to([3.2, -0.6, 0])

        with self.voice("On met les flèches bout à bout. Si on revient au point de départ, "
                        "la somme est nulle et R vaut zéro."):
            self.play(FadeOut(VGroup(a4, a2, arc4, arc2, lab, unit)), run_time=0.5)
            self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.6), run_time=2.4)
            self.play(GrowArrow(total), FadeIn(rule), run_time=1.0)

        # ----- [0/45] for R0 -----
        self.play(FadeOut(VGroup(arrows, total, rule, ax)), FadeOut(pair), run_time=0.5)
        c1 = np.array([-3.4, 0.2, 0])
        ax1 = complex_axes(c1, 2.0)
        ar45, _ = chain([0, 45], 4, c1 + LEFT * 0.8, 1.6)
        t45 = tex(r"$[0/45]$, flèches à $4\delta$ : $0^\circ$ et $180^\circ$\\$\Rightarrow R_0^{A^*} = 0$",
                  30, FG).next_to(ax1, DOWN, buff=0.3)
        # the second arrow comes back over the first: shift it slightly to show both
        ar45[1].shift(UP * 0.08)

        with self.voice("Un pli à 0 et un pli à 45 degrés : pour R0, les flèches pointent à 0 "
                        "et à 180 degrés, elles s'annulent."):
            self.play(FadeIn(ax1), run_time=0.4)
            self.play(LaggedStart(*[GrowArrow(a) for a in ar45], lag_ratio=0.8), run_time=1.6)
            self.play(FadeIn(t45), Indicate(Dot(c1 + LEFT * 0.8, color=ACCENT), scale_factor=2), run_time=1.0)

        # ----- [0/60/-60] for R0 and R1 -----
        c2 = np.array([1.0, 0.4, 0])
        c3 = np.array([4.6, 0.4, 0])
        ax2, ax3 = complex_axes(c2, 1.7), complex_axes(c3, 1.7)
        tri4, _ = chain([0, 60, -60], 4, c2 + np.array([-0.7, -0.4, 0]), 1.4)
        tri2, _ = chain([0, 60, -60], 2, c3 + np.array([-0.7, -0.4, 0]), 1.4)
        t4 = tex(r"$4\delta$ : triangle fermé", 28, FG).next_to(ax2, DOWN, buff=0.2)
        t2 = tex(r"$2\delta$ : triangle fermé", 28, FG).next_to(ax3, DOWN, buff=0.2)
        head = tex(r"$[0/60/{-60}]$ : $R_0^{A^*} = R_1^{A^*} = 0$, membrane isotrope", 32, ACCENT
                   ).move_to([2.8, 2.7, 0])

        with self.voice("Avec 0, 60 et moins 60 degrés, les flèches forment un triangle fermé, "
                        "pour R0 comme pour R1, et la membrane est isotrope."):
            self.play(FadeIn(ax2), FadeIn(ax3), FadeIn(head), run_time=0.5)
            self.play(LaggedStart(*[GrowArrow(a) for a in tri4], lag_ratio=0.7), run_time=1.6)
            self.play(LaggedStart(*[GrowArrow(a) for a in tri2], lag_ratio=0.7), run_time=1.6)
            self.play(FadeIn(t4), FadeIn(t2), run_time=0.6)

        # ----- weights b_k reopen the sum (B*, n = 3: b = -2, 0, 2) -----
        n = 3
        b = np.array([2 * k - n - 1 for k in range(1, n + 1)], float)
        tri4_b, end_b = chain([0, 60, -60], 4, c2 + np.array([-0.7, -0.4, 0]), 1.4 * 0.5, b)
        start_b = c2 + np.array([-0.7, -0.4, 0])
        gap = Arrow(start_b, end_b, buff=0, color=COL_B, stroke_width=5)
        wlab = math(r"\mathbf{B}^*:\ \frac{1}{n^2}R_0e^{4i\Phi_0}\sum_k b_k\,e^{4i\delta_k},"
                    r"\qquad b_k = 2k-n-1 = -2,\ 0,\ 2", 32, COL_B).move_to([0, -3.0, 0])
        open_lab = tex(r"avec les poids :\\la somme se rouvre", 26, COL_B).next_to(ax2, DOWN, buff=0.2)

        with self.voice("Pour B étoile et D étoile, chaque flèche est en plus multipliée par "
                        "un poids qui dépend de la place du pli."):
            self.play(FadeOut(VGroup(ax1, ar45, t45)), FadeIn(wlab), run_time=0.8)
            self.play(ReplacementTransform(tri4, tri4_b), Transform(t4, open_lab), run_time=1.6)
            self.play(GrowArrow(gap), run_time=0.8)

        # ----- 20 angles, three sums with different weights -----
        rng = np.random.default_rng(3)
        angles = rng.integers(-89, 91, 20)
        N = 20
        z = np.arange(N + 1) - N / 2
        weights = {
            r"$\mathbf{A}^*$, $R_0$ ($4\delta$)": (4, np.ones(N), COL_A),
            r"$\mathbf{B}^*$, $R_0$ ($4\delta$, $b_k$)": (4, z[1:]**2 - z[:-1]**2, COL_B),
            r"$\mathbf{D}^*$, $R_1$ ($2\delta$, $d_k$)": (2, 4 * (z[1:]**3 - z[:-1]**3), COL_D),
        }
        panels = VGroup()
        centers = [np.array([-4.3, -0.2, 0]), np.array([0, -0.2, 0]), np.array([4.3, -0.2, 0])]
        for (label, (f, w, col)), cc in zip(weights.items(), centers):
            w = w / np.abs(w).mean()                 # same average arrow length in each panel
            arr, end = arrow_chain(np.radians(f * angles), w, origin=cc, scale=0.32, colors=[col])
            arr.move_to(cc)
            panels.add(VGroup(arr, tex(label, 26, col).move_to(cc + DOWN * 2.6)))
        last = tex(r"les \emph{mêmes} 20 angles doivent refermer toutes ces sommes", 34, ACCENT
                   ).to_edge(UP, buff=0.5)

        with self.voice("C'est là toute la difficulté : les mêmes vingt angles doivent refermer "
                        "plusieurs sommes, chacune avec ses propres poids."):
            self.play(FadeOut(VGroup(ax2, ax3, tri4_b, gap, tri2, t4, t2, head, wlab)),
                      run_time=0.6)
            self.play(FadeIn(last), run_time=0.6)
            for p in panels:
                self.play(LaggedStart(*[GrowArrow(a) for a in p[0]], lag_ratio=0.15), FadeIn(p[1]),
                          run_time=1.3)
