"""
Scene 2 - The ply (scenario.md, about 0:50).

A single ply seen from above: fibres and resin, pulling along and across the
fibres (E1, E2 compared with steel), orthotropy, then the ply orientation
delta, why 100 deg and -80 deg are the same fibre, and the 180 allowed values.
Material data come from config.py.
"""

from manim import (
    DEGREES, Arc, Arrow, Create, DashedLine, Dot, FadeIn, FadeOut, GrowArrow,
    GrowFromEdge, Line, Rectangle, Rotate, Square, VGroup, Write, Circle,
    LaggedStart, Indicate,
)

from common import (
    ACCENT, COL_Q, COL_RESIN, DOWN, FG, LEFT, MUTED, RIGHT, UP, NarratedScene,
    config, fibre_hatch, math, np, tex,
)

PLY_C = np.array([-3.6, 0.2, 0.0])
PLY_SIZE = 3.0
STEEL = 210000.0                 # MPa, order of magnitude used in the narration
BAR_X0, BAR_LEN = 0.6, 4.3       # bar chart: start x and length of 210 000 MPa


def mpa(value):
    """161000 -> '161\\,000'."""
    return f"{int(round(value)):,}".replace(",", r"\,")


def bar(value, y, color, label, value_text):
    w = max(BAR_LEN * value / STEEL, 0.04)
    rect = Rectangle(width=w, height=0.42, stroke_width=0, fill_color=color, fill_opacity=0.9)
    rect.move_to([BAR_X0 + w / 2, y, 0])
    name = tex(label, 28, FG).next_to(rect, UP, buff=0.12, aligned_edge=LEFT)
    val = tex(value_text, 26, FG).next_to(rect, RIGHT, buff=0.15)
    return VGroup(rect, name, val)


class S02Ply(NarratedScene):
    def construct(self):
        # ----- the ply, fibres along x -----
        resin = Square(PLY_SIZE, stroke_width=0, fill_color=COL_RESIN, fill_opacity=0.85).move_to(PLY_C)
        fibres = fibre_hatch(PLY_C, PLY_SIZE, PLY_SIZE, 0.0, spacing=0.12, stroke=2.2)
        ply = VGroup(resin, fibres)

        lab_fib = tex("fibres de carbone", 26, FG).next_to(resin, UP, buff=0.35).shift(LEFT * 0.6)
        lab_res = tex("résine époxyde", 26, FG).next_to(resin, DOWN, buff=0.35).shift(RIGHT * 0.6)
        ar_fib = Arrow(lab_fib.get_bottom(), PLY_C + np.array([-0.7, 1.08, 0]), buff=0.05,
                       color=FG, stroke_width=3, max_tip_length_to_length_ratio=0.25)
        ar_res = Arrow(lab_res.get_top(), PLY_C + np.array([0.8, -1.02, 0]), buff=0.05,
                       color=FG, stroke_width=3, max_tip_length_to_length_ratio=0.25)

        with self.voice("Commençons par une seule couche, un pli. C'est une feuille de "
                        "fibres de carbone toutes parallèles, collées par une résine époxyde."):
            self.play(FadeIn(resin), run_time=0.8)
            self.play(LaggedStart(*[Create(l) for l in fibres], lag_ratio=0.04), run_time=1.6)
            self.play(FadeIn(lab_fib), GrowArrow(ar_fib), run_time=0.7)
            self.play(FadeIn(lab_res), GrowArrow(ar_res), run_time=0.7)

        # ----- pulling along the fibres: E1 vs steel -----
        half = PLY_SIZE / 2
        pull_1 = VGroup(
            Arrow(PLY_C + RIGHT * (half + 0.05), PLY_C + RIGHT * (half + 1.0), buff=0, color=ACCENT, stroke_width=7),
            Arrow(PLY_C + LEFT * (half + 0.05), PLY_C + LEFT * (half + 1.0), buff=0, color=ACCENT, stroke_width=7),
        )
        bar_e1 = bar(config.E1, 1.5, COL_Q, r"$E_1$ (sens des fibres)", mpa(config.E1) + r"~MPa")
        bar_steel = bar(STEEL, 0.3, MUTED, r"acier (pour comparer)", mpa(STEEL) + r"~MPa")

        with self.voice("Si on tire dans le sens des fibres, le module vaut 161 000 MPa. "
                        "L'acier, pour comparer, est à 210 000."):
            self.play(FadeOut(lab_fib, ar_fib, lab_res, ar_res), run_time=0.4)
            self.play(*[GrowArrow(a) for a in pull_1], run_time=0.7)
            self.play(GrowFromEdge(bar_e1[0], LEFT), FadeIn(bar_e1[1:]), run_time=1.0)
            self.play(GrowFromEdge(bar_steel[0], LEFT), FadeIn(bar_steel[1:]), run_time=1.0)

        # ----- pulling across: E2 -----
        pull_2 = VGroup(
            Arrow(PLY_C + UP * (half + 0.05), PLY_C + UP * (half + 0.9), buff=0, color=ACCENT, stroke_width=7),
            Arrow(PLY_C + DOWN * (half + 0.05), PLY_C + DOWN * (half + 0.9), buff=0, color=ACCENT, stroke_width=7),
        )
        bar_e2 = bar(config.E2, -0.9, COL_Q, r"$E_2$ (en travers)", mpa(config.E2) + r"~MPa")
        ratio = math(r"\div\,18", 40, ACCENT).next_to(bar_e2[2], RIGHT, buff=0.4)

        with self.voice("Si on tire en travers, on tombe à 9 000, dix-huit fois moins."):
            self.play(FadeOut(pull_1), run_time=0.3)
            self.play(*[GrowArrow(a) for a in pull_2], run_time=0.7)
            self.play(GrowFromEdge(bar_e2[0], LEFT), FadeIn(bar_e2[1:]), run_time=0.8)
            self.play(Write(ratio), run_time=0.6)

        # ----- orthotropy: axes 1 and 2 -----
        ax1 = Arrow(PLY_C, PLY_C + RIGHT * 2.1, buff=0, color=ACCENT, stroke_width=5)
        ax2 = Arrow(PLY_C, PLY_C + UP * 2.1, buff=0, color=ACCENT, stroke_width=5)
        l1 = tex("1 (fibres)", 28, ACCENT).next_to(ax1.get_end(), DOWN, buff=0.12)
        l2 = tex(r"2 ($\perp$ fibres)", 28, ACCENT).next_to(ax2.get_end(), UP, buff=0.12)
        ortho = tex(r"deux directions privilégiées\\perpendiculaires : \emph{orthotrope}",
                    32, FG).move_to([3.2, -2.5, 0])

        with self.voice("Le pli a deux directions privilégiées, perpendiculaires : on dit qu'il "
                        "est orthotrope. On les appelle 1, le long des fibres, et 2, en travers."):
            self.play(FadeOut(pull_2), run_time=0.3)
            self.play(GrowArrow(ax1), GrowArrow(ax2), run_time=0.9)
            self.play(FadeIn(ortho, shift=0.2 * UP), run_time=0.8)
            self.play(FadeIn(l1), FadeIn(l2), run_time=0.8)

        # ----- two frames: plate (x, y), fixed; ply (1, 2), rotating -----
        delta = 30.0
        x_ax = Arrow(PLY_C + LEFT * 2.3, PLY_C + RIGHT * 2.5, buff=0, color=MUTED, stroke_width=3)
        y_ax = Arrow(PLY_C + DOWN * 2.3, PLY_C + UP * 2.5, buff=0, color=MUTED, stroke_width=3)
        lx = tex(r"$x$ (plaque)", 28, MUTED).next_to(x_ax.get_end(), RIGHT, buff=0.1)
        ly = tex(r"$y$ (plaque)", 28, MUTED).next_to(y_ax.get_end(), LEFT, buff=0.1)
        plate_axes = VGroup(x_ax, y_ax, lx, ly)
        arc = Arc(radius=1.0, start_angle=0, angle=delta * DEGREES, arc_center=PLY_C, color=ACCENT, stroke_width=4)
        l_delta = math(r"\delta", 36, ACCENT).move_to(PLY_C + 1.3 * np.array(
            [np.cos(np.radians(delta / 2)), np.sin(np.radians(delta / 2)), 0]))
        info_delta = tex(r"$\delta$ : angle entre l'axe $x$ de la plaque\\et les fibres (axe 1)",
                         30, FG).move_to([3.4, 2.3, 0])
        frames = VGroup(tex(r"$x, y$ : axes de la plaque, fixes,\\les mêmes pour tous les plis", 28, MUTED),
                        tex(r"$1, 2$ : axes du pli,\\ils tournent avec lui", 28, ACCENT)
                        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([3.4, 0.6, 0])

        with self.voice("Chaque pli est posé avec ses fibres tournées d'un angle delta par "
                        "rapport à l'axe x de la plaque. Les axes x et y sont fixes ; les axes 1 "
                        "et 2 tournent avec le pli."):
            self.play(FadeOut(bar_e1, bar_steel, bar_e2, ratio, ortho, l1, l2), run_time=0.5)
            self.add(plate_axes)
            self.bring_to_back(plate_axes)
            self.play(FadeIn(plate_axes), run_time=0.5)
            self.play(Rotate(VGroup(ply, ax1, ax2), angle=delta * DEGREES, about_point=PLY_C),
                      run_time=1.6)
            l1.next_to(ax1.get_end(), RIGHT, buff=0.1)
            l2.next_to(ax2.get_end(), UP, buff=0.1)
            self.play(Create(arc), Write(l_delta), FadeIn(info_delta), FadeIn(l1), FadeIn(l2),
                      run_time=0.9)
            self.play(FadeIn(frames, shift=0.2 * UP), run_time=0.8)

        # ----- examples 0, 90, 45 deg and which frame each quantity lives in -----
        examples = VGroup()
        for i, (a, txt) in enumerate(((0, r"fibres selon $x$"), (90, r"fibres selon $y$"),
                                      (45, r"en diagonale"))):
            c = np.array([1.2 + 2.0 * i, -0.4, 0])
            sq = VGroup(Square(1.0, stroke_width=1, stroke_color=MUTED, fill_color=COL_RESIN,
                               fill_opacity=0.85).move_to(c),
                        fibre_hatch(c, 1.0, 1.0, a, spacing=0.14, stroke=2))
            examples.add(VGroup(sq, math(rf"\delta = {a}^\circ", 28, FG).next_to(sq, UP, buff=0.12),
                                tex(txt, 22, MUTED).next_to(sq, DOWN, buff=0.12)))
        where = VGroup(tex(r"$E_1, E_2, G_{12}, \nu_{12}$ : dans les axes du pli $(1, 2)$", 28, ACCENT),
                       tex(r"$\mathbf{A}, \mathbf{B}, \mathbf{D}$ : dans les axes de la plaque $(x, y)$", 28, MUTED),
                       tex(r"passer de l'un à l'autre $=$ tourner le pli de $\delta$", 28, FG)
                       ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to([3.2, -2.6, 0])

        with self.voice("Les constantes du pli sont données dans ses axes 1 et 2, les rigidités "
                        "de la plaque dans les axes x et y : on passe des uns aux autres en "
                        "tournant le pli de delta."):
            self.play(FadeOut(frames), info_delta.animate.move_to([3.4, 2.6, 0]), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(e) for e in examples], lag_ratio=0.5), run_time=1.4)
            self.play(LaggedStart(*[FadeIn(w, shift=0.2 * RIGHT) for w in where], lag_ratio=0.6),
                      run_time=2.0)

        # ----- 100 deg and -80 deg are the same fibre -----
        def fibre_line(angle_deg, color, length=4.6):
            a = np.radians(angle_deg)
            d = np.array([np.cos(a), np.sin(a), 0])
            return Line(PLY_C - d * length / 2, PLY_C + d * length / 2, color=color, stroke_width=6)

        f100 = fibre_line(100, ACCENT)
        f_80 = DashedLine(f100.get_start(), f100.get_end(), color=COL_Q, stroke_width=6, dash_length=0.18)
        arc100 = Arc(radius=0.9, start_angle=0, angle=100 * DEGREES, arc_center=PLY_C, color=ACCENT, stroke_width=4)
        arc_80 = Arc(radius=1.25, start_angle=0, angle=-80 * DEGREES, arc_center=PLY_C, color=COL_Q, stroke_width=4)
        t100 = math(r"100^\circ", 30, ACCENT).move_to(PLY_C + np.array([0.7, 1.15, 0]))
        t_80 = math(r"-80^\circ", 30, COL_Q).move_to(PLY_C + np.array([1.35, -1.25, 0]))
        same = tex(r"Une fibre n'a pas de sens :\\$100^\circ$ et $-80^\circ$, même fibre",
                   32, FG).move_to([3.2, 1.2, 0])

        with self.voice("Une fibre n'a pas de sens : 100 degrés et moins 80 degrés, "
                        "c'est la même fibre."):
            self.play(FadeOut(arc, l_delta, info_delta, ax1, ax2, l1, l2, examples, where),
                      ply.animate.set_opacity(0.25),
                      run_time=0.6)
            self.play(Create(f100), Create(arc100), FadeIn(t100), FadeIn(same), run_time=1.0)
            self.play(Create(f_80), Create(arc_80), FadeIn(t_80), run_time=1.0)
            self.play(Indicate(VGroup(f100, f_80), color=FG, scale_factor=1.05), run_time=0.8)

        # ----- ]-90, 90], 180 values -----
        x0, x1, y = 0.6, 6.4, -1.0
        span = x1 - x0

        def xpos(a):
            return x0 + span * (a + 90) / 180

        base = Line([x0, y, 0], [x1, y, 0], color=MUTED, stroke_width=2)
        ticks = VGroup(*[
            Line([xpos(a), y - (0.16 if a % 10 == 0 else 0.08), 0],
                 [xpos(a), y + (0.16 if a % 10 == 0 else 0.08), 0],
                 color=ACCENT if a % 10 == 0 else FG, stroke_width=1.6 if a % 10 == 0 else 1.0)
            for a in range(-89, 91)
        ])
        open_end = Circle(radius=0.07, color=FG, stroke_width=2).move_to([xpos(-90), y, 0])
        closed_end = Dot([xpos(90), y, 0], radius=0.07, color=FG)
        tick_labels = VGroup(*[
            math(f"{a}^\\circ", 24, MUTED).next_to([xpos(a), y - 0.2, 0], DOWN, buff=0.1)
            for a in (-90, -45, 0, 45, 90)
        ])
        interval = math(r"\delta \in \left]-90^\circ,\ 90^\circ\right]", 38, FG).move_to([3.5, 0.3, 0])
        count = tex(r"pas de $1^\circ$ : \textbf{180 valeurs}", 32, ACCENT).move_to([3.5, -2.3, 0])

        with self.voice("Delta va donc de moins 89 à 90 degrés, au pas de 1 degré. "
                        "Ça fait 180 valeurs."):
            self.play(FadeOut(same), run_time=0.3)
            self.play(Write(interval), Create(base), FadeIn(tick_labels), run_time=0.9)
            self.play(LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.01),
                      FadeIn(open_end), FadeIn(closed_end), run_time=2.0)
            self.play(FadeIn(count, shift=0.2 * UP), run_time=0.6)
