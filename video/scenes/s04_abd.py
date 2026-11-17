"""
Scene 4 - A, B, D and the homogenised matrices (scenario.md, about 0:55).

A plate stretched (membrane) then bent (bending), the CLT equations, a plate
that bends when pulled (B != 0), then the weight of each ply in A, D and B
as bars next to the 20-ply cross-section, and A*, B*, D*.
The weights are the exact ones of laminate.abd_matrices (n = 20).
"""

from manim import (
    Arrow, Create, DashedLine, FadeIn, FadeOut, Indicate, Polygon, Rectangle,
    SurroundingRectangle, Transform, ValueTracker, VGroup, Write, always_redraw,
    LaggedStart, GrowArrow, CurvedArrow, PI,
)

from common import (
    ACCENT, COL_A, COL_B, COL_D, COL_RESIN, DOWN, FG, LEFT, MUTED, RIGHT, UP,
    NarratedScene, config, math, np, tex,
)

N = config.N_PLIES
PLATE_C = np.array([0.0, 1.6, 0.0])
PLATE_L, PLATE_T = 6.0, 0.35


def plate_shape(kappa, stretch):
    """Side view of a plate of length PLATE_L, bent with curvature kappa and
    stretched by the factor `stretch`, as a polygon centred on PLATE_C."""
    s = np.linspace(-PLATE_L / 2, PLATE_L / 2, 60) * stretch
    if abs(kappa) < 1e-6:
        p = np.stack([s, np.zeros_like(s)], 1)
        nrm = np.tile([0.0, 1.0], (s.size, 1))
    else:
        p = np.stack([np.sin(kappa * s) / kappa, (1 - np.cos(kappa * s)) / kappa], 1)
        nrm = np.stack([-np.sin(kappa * s), np.cos(kappa * s)], 1)
    top = p + nrm * PLATE_T / 2
    bot = p - nrm * PLATE_T / 2
    pts = np.vstack([top, bot[::-1]])
    pts = np.hstack([pts, np.zeros((pts.shape[0], 1))]) + PLATE_C
    return Polygon(*pts, stroke_width=1.5, stroke_color=FG, fill_color=COL_RESIN, fill_opacity=0.85)


class S04ABD(NarratedScene):
    def construct(self):
        kappa = ValueTracker(0.0)
        stretch = ValueTracker(1.0)
        plate = always_redraw(lambda: plate_shape(kappa.get_value(), stretch.get_value()))

        def end_arrows(color):
            """Pulling arrows attached to the two ends of the plate."""
            def build():
                pts = plate_shape(kappa.get_value(), stretch.get_value()).get_vertices()
                n = len(pts) // 2
                right = (pts[n - 1] + pts[n]) / 2
                left = (pts[0] + pts[-1]) / 2
                return VGroup(
                    Arrow(right, right + RIGHT * 1.0, buff=0.05, color=color, stroke_width=6),
                    Arrow(left, left + LEFT * 1.0, buff=0.05, color=color, stroke_width=6),
                )
            return always_redraw(build)

        lab_mem = tex(r"\textbf{membrane} : on tire dans le plan ($\mathbf{N}$),\\"
                      r"la plaque s'allonge et reste plate $\rightarrow$ rigidité $\mathbf{A}$",
                      30, FG).move_to([0, -0.5, 0])
        lab_fle = tex(r"\textbf{flexion} : on plie la plaque ($\mathbf{M}$),\\"
                      r"elle se courbe $\rightarrow$ rigidité $\mathbf{D}$", 30, FG).move_to([0, -0.5, 0])
        pull = end_arrows(ACCENT)

        def moments(k):
            """Curved arrows (bending moments M) at both ends of the plate bent with curvature k."""
            pts = plate_shape(k, 1.0).get_vertices()
            n = len(pts) // 2
            right, left = (pts[n - 1] + pts[n]) / 2, (pts[0] + pts[-1]) / 2
            return VGroup(
                CurvedArrow(right + np.array([0.35, -0.45, 0]), right + np.array([0.35, 0.45, 0]),
                            angle=PI * 0.8, color=ACCENT, stroke_width=5),
                CurvedArrow(left + np.array([-0.35, -0.45, 0]), left + np.array([-0.35, 0.45, 0]),
                            angle=-PI * 0.8, color=ACCENT, stroke_width=5),
            )

        with self.voice("On empile maintenant les vingt plis. Une plaque travaille de deux "
                        "façons : en membrane, quand on la tire dans son plan, et en flexion, "
                        "quand on la courbe."):
            self.play(FadeIn(plate), run_time=0.6)
            self.add(pull)
            self.play(stretch.animate.set_value(1.08), FadeIn(lab_mem), run_time=1.4)
            self.wait(0.6)
            self.remove(pull)
            self.play(stretch.animate.set_value(1.0), FadeOut(lab_mem), run_time=0.6)
            m_arrows = moments(0.28)
            self.play(FadeIn(m_arrows), kappa.animate.set_value(0.28), FadeIn(lab_fle), run_time=1.4)
            self.wait(0.6)
            self.play(kappa.animate.set_value(0.0), FadeOut(lab_fle), FadeOut(m_arrows), run_time=0.6)

        eqs = math(r"\mathbf{N} &= \mathbf{A}\,\boldsymbol{\varepsilon}_0 + \mathbf{B}\,\boldsymbol{\chi}\\"
                   r"\mathbf{M} &= \mathbf{B}\,\boldsymbol{\varepsilon}_0 + \mathbf{D}\,\boldsymbol{\chi}",
                   50, substrings_to_isolate=[r"\mathbf{A}", r"\mathbf{B}", r"\mathbf{D}"]
                   ).move_to([-2.6, -1.4, 0])
        eqs.set_color_by_tex(r"\mathbf{A}", COL_A)
        eqs.set_color_by_tex(r"\mathbf{B}", COL_B)
        eqs.set_color_by_tex(r"\mathbf{D}", COL_D)
        legend = VGroup(
            tex(r"$\mathbf{A}$ : rigidité de membrane", 30, COL_A),
            tex(r"$\mathbf{D}$ : rigidité de flexion", 30, COL_D),
            tex(r"$\mathbf{B}$ : couplage membrane / flexion", 30, COL_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([3.4, -1.4, 0])

        with self.voice("La théorie classique des stratifiés relie les deux avec trois "
                        "matrices. A est la rigidité de membrane, D celle de flexion, et B "
                        "le couplage."):
            self.play(Write(eqs), run_time=1.8)
            self.play(LaggedStart(*[FadeIn(l, shift=0.2 * RIGHT) for l in legend], lag_ratio=0.5),
                      run_time=2.2)

        pull_b = end_arrows(COL_B)
        warn = tex(r"$\mathbf{B} \neq 0$ : on ne fait que tirer, et la plaque se courbe\\"
                   r"c'est ce que supprimera l'objectif $\Phi_1$ ($\mathbf{B}^* = 0$)", 30, COL_B
                   ).move_to([0, -0.1, 0])

        with self.voice("Si B n'est pas nul, tirer sur la plaque la fait aussi se courber. "
                        "C'est ce que l'objectif Phi1 devra supprimer."):
            self.add(pull_b)
            self.play(stretch.animate.set_value(1.06), kappa.animate.set_value(0.22),
                      FadeIn(warn), Indicate(legend[2]), run_time=1.8)

        # ----- weights of each ply -----
        self.remove(pull_b)
        z = np.arange(N + 1) - N / 2              # interfaces z_k / t
        w_A = np.ones(N)
        w_B = z[1:]**2 - z[:-1]**2                # = 2k - n - 1
        w_D = z[1:]**3 - z[:-1]**3

        sh, gap = 0.2, 0.04
        y0 = -(N * (sh + gap) - gap) / 2 + sh / 2 - 0.2
        stack_x = -3.6
        strips = VGroup(*[
            Rectangle(width=2.6, height=sh, stroke_width=0, fill_color=COL_RESIN,
                      fill_opacity=0.9 if k % 2 else 0.7).move_to([stack_x, y0 + k * (sh + gap), 0])
            for k in range(N)
        ])
        mid = DashedLine([stack_x - 1.7, y0 + (N - 1) * (sh + gap) / 2, 0],
                         [stack_x + 1.7, y0 + (N - 1) * (sh + gap) / 2, 0], color=ACCENT)
        zax = Arrow([stack_x - 1.8, y0 - 0.3, 0], [stack_x - 1.8, y0 + N * (sh + gap) + 0.1, 0],
                    buff=0, color=MUTED, stroke_width=3)
        zl = math("z", 30, MUTED).next_to(zax.get_end(), UP, buff=0.05)
        bar_x0, bar_max = 2.6, 2.6

        def bars(weights, color):
            m = np.max(np.abs(weights))
            out = VGroup()
            for k, w in enumerate(weights):
                L = bar_max * w / m
                r = Rectangle(width=max(abs(L), 0.02), height=sh, stroke_width=0,
                              fill_color=color, fill_opacity=0.9)
                r.move_to([bar_x0 + L / 2, y0 + k * (sh + gap), 0])
                out.add(r)
            return out

        axis0 = DashedLine([bar_x0, y0 - 0.25, 0], [bar_x0, y0 + N * (sh + gap), 0], color=MUTED)
        bars_now = bars(w_A, COL_A)
        cap = tex(r"$\mathbf{A}$ : $\sum_k \mathbf{Q}_k\,(z_k - z_{k-1})$ \quad tous les plis pareil",
                  30, COL_A).move_to([3.0, 3.3, 0])

        with self.voice("Chaque pli compte selon sa hauteur z dans l'épaisseur. Dans A, "
                        "tous les plis pèsent pareil."):
            self.play(FadeOut(plate, eqs, legend, warn), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(s) for s in strips], lag_ratio=0.03),
                      Create(zax), FadeIn(zl), Create(mid), run_time=1.2)
            self.play(Create(axis0), LaggedStart(*[FadeIn(b) for b in bars_now], lag_ratio=0.03),
                      FadeIn(cap), run_time=1.4)

        cap_d = tex(r"$\mathbf{D}$ : $\frac13\sum_k \mathbf{Q}_k\,(z_k^3 - z_{k-1}^3)$ \quad l'extérieur domine",
                    30, COL_D).move_to(cap)
        with self.voice("Dans D, le poids va en z au cube, donc les plis de l'extérieur dominent."):
            self.play(Transform(bars_now, bars(w_D, COL_D)), Transform(cap, cap_d), run_time=1.5)

        cap_b = tex(r"$\mathbf{B}$ : $\frac12\sum_k \mathbf{Q}_k\,(z_k^2 - z_{k-1}^2)$ \quad signe opposé",
                    30, COL_B).move_to(cap)
        pair = VGroup(SurroundingRectangle(VGroup(strips[2], bars(w_B, COL_B)[2]), color=ACCENT, buff=0.05),
                      SurroundingRectangle(VGroup(strips[N - 3], bars(w_B, COL_B)[N - 3]), color=ACCENT, buff=0.05))
        with self.voice("Dans B, le poids va en z carré avec un signe : un pli en bas et le "
                        "même pli en haut s'annulent."):
            self.play(Transform(bars_now, bars(w_B, COL_B)), Transform(cap, cap_b), run_time=1.5)
            self.play(Create(pair), run_time=0.8)

        star = math(r"\mathbf{A}^* = \frac{\mathbf{A}}{h} \qquad \mathbf{B}^* = \frac{2\,\mathbf{B}}{h^2}"
                    r"\qquad \mathbf{D}^* = \frac{12\,\mathbf{D}}{h^3}", 48)
        star_note = tex(r"en MPa, comparables à $\mathbf{Q}$ \quad ($h = 20 \times 0{,}125 = 2{,}5$ mm)",
                        30, MUTED).next_to(star, DOWN, buff=0.5)
        with self.voice("On divise enfin par l'épaisseur pour obtenir A étoile, B étoile et "
                        "D étoile, en mégapascals, comparables au pli."):
            self.play(FadeOut(VGroup(strips, mid, zax, zl, axis0, bars_now, cap, pair)), run_time=0.6)
            self.play(Write(star), run_time=1.6)
            self.play(FadeIn(star_note), run_time=0.6)
