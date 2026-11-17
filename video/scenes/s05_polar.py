"""
Scene 5 - The polar method (scenario.md, about 0:50).

The Cartesian components of Q change when the frame rotates; the six polar
parameters; T0, T1, R0, R1 are invariants; the polar diagram of the ply
then morphs through the shapes of P2 slide 38 (R0 = 0, R1 = 0, isotropy).
Polar parameters of the ply come from polar.py.
"""

from manim import (
    DEGREES, Arrow, Circle, Create, DecimalNumber, FadeIn, FadeOut, Indicate,
    LaggedStart, SurroundingRectangle, Transform, ValueTracker, VGroup, Write,
    always_redraw, Line, DashedLine,
)

from common import (
    ACCENT, COL_A, COL_B, COL_D, COL_Q, DOWN, FG, LEFT, MUTED, RIGHT, UP,
    NarratedScene, config, math, np, polar_curve, tex,
)

import laminate as lam  # project code, read-only
import polar as pol

Q = lam.ply_stiffness(lam.ply_compliance(config.E1, config.E2, config.NU12, config.G12))
PP_Q = pol.polar_parameters(Q)
SCALE = 2.6 / 161611.0          # radius of the ply diagram at 0 deg = 2.6 units
DIAG_C = np.array([-3.2, -0.4, 0.0])


class S05Polar(NarratedScene):
    def construct(self):
        # ----- Cartesian components change with the frame -----
        theta = ValueTracker(0.0)
        frame_c = np.array([-3.5, 0.0, 0.0])

        def frame():
            t = np.radians(theta.get_value())
            ex = np.array([np.cos(t), np.sin(t), 0]) * 1.8
            ey = np.array([-np.sin(t), np.cos(t), 0]) * 1.8
            return VGroup(Arrow(frame_c, frame_c + ex, buff=0, color=ACCENT, stroke_width=5),
                          Arrow(frame_c, frame_c + ey, buff=0, color=ACCENT, stroke_width=5))

        axes = always_redraw(frame)
        fibre = VGroup(*[Line(frame_c + np.array([-2.2, y, 0]), frame_c + np.array([2.2, y, 0]),
                              color=MUTED, stroke_width=1.5) for y in np.linspace(-1.6, 1.6, 9)])

        def matrix():
            Qr = lam.rotate_stiffness(Q, -theta.get_value())[0]   # ply seen from the rotated frame
            cells = VGroup()
            for i in range(3):
                for j in range(3):
                    cells.add(DecimalNumber(Qr[i, j] / 1000, num_decimal_places=1, font_size=34,
                                            color=FG).move_to([1.6 + 1.5 * j, 1.0 - 0.75 * i, 0]))
            return cells

        cells = always_redraw(matrix)
        def bracket(x, sign):
            top, bot = 1.45, -0.95
            return VGroup(Line([x, top, 0], [x, bot, 0], color=FG, stroke_width=3),
                          Line([x, top, 0], [x + sign * 0.18, top, 0], color=FG, stroke_width=3),
                          Line([x, bot, 0], [x + sign * 0.18, bot, 0], color=FG, stroke_width=3))

        brackets = VGroup(bracket(0.8, 1), bracket(5.4, -1))
        unit = tex(r"composantes de $\mathbf{Q}$ (GPa) vues dans le repère tourné", 26, MUTED
                   ).move_to([3.1, -1.3, 0])

        with self.voice("Le problème de ces matrices, c'est que leurs composantes changent dès "
                        "qu'on tourne les axes. Difficile de voir si une plaque est isotrope "
                        "rien qu'en les regardant."):
            self.play(FadeIn(fibre), FadeIn(axes), FadeIn(cells), FadeIn(brackets), FadeIn(unit),
                      run_time=0.8)
            self.play(theta.animate.set_value(90), run_time=4.0)
            self.play(theta.animate.set_value(35), run_time=2.0)

        # ----- the six polar parameters -----
        table = VGroup(
            tex(r"$T_0,\ T_1$ : modules isotropes", 34, FG),
            tex(r"$R_0,\ R_1$ : modules anisotropes", 34, FG),
            tex(r"$\Phi_0,\ \Phi_1$ : angles polaires", 34, FG),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45).to_edge(LEFT, buff=0.8).shift(UP * 0.3)
        head = tex(r"Verchery (1979) : six autres nombres pour le même tenseur", 34, ACCENT
                   ).to_edge(UP, buff=0.6)

        # "L" is a generic name, not a new matrix (explication_du_sujet, section 4.2)
        generic = tex(r"$\mathbf{L}$ = n'importe laquelle de nos matrices : "
                      r"$\mathbf{Q}$, $\mathbf{A}^*$, $\mathbf{B}^*$, $\mathbf{D}^*$ ou "
                      r"$\mathbf{C} = \mathbf{A}^* - \mathbf{D}^*$", 30, COL_Q).next_to(head, DOWN, buff=0.3)

        with self.voice("En 1979, Verchery propose de réécrire chacune de ces matrices avec six "
                        "autres nombres. La recette est la même pour Q, A étoile, B étoile ou D "
                        "étoile : dans les formules, on appelle simplement L la matrice traitée."):
            self.play(FadeOut(VGroup(fibre, axes, cells, brackets, unit)), run_time=0.6)
            self.play(FadeIn(head), LaggedStart(*[FadeIn(r, shift=0.2 * RIGHT) for r in table],
                                                lag_ratio=0.4), run_time=1.8)
            self.play(FadeIn(generic, shift=0.2 * DOWN), run_time=0.8)

        notes = [
            tex(r"la partie identique dans toutes les directions", 26, COL_Q),
            tex(r"de combien la rigidité varie avec la direction", 26, COL_Q),
            tex(r"où sont les maxima", 28, COL_Q),
        ]
        texts = [
            "T0 et T1 sont la partie isotrope, la même dans toutes les directions.",
            "R0 et R1 disent de combien la rigidité varie avec la direction.",
            "Phi0 et Phi1 sont des angles, qui disent où sont les maxima.",
        ]
        for row, note, text in zip(table, notes, texts):
            note.next_to(row, RIGHT, buff=0.4)
            with self.voice(text):
                self.play(Indicate(row, color=ACCENT, scale_factor=1.05), FadeIn(note), run_time=1.2)

        inv = SurroundingRectangle(VGroup(table[0], table[1]), color=COL_A, buff=0.15)
        inv_lab = tex(r"invariants : ne changent pas quand on tourne les axes", 28, COL_A
                      ).next_to(table, DOWN, buff=0.6)
        formulas = math(r"8T_0 = L_{11}-2L_{12}+4L_{66}+L_{22} \qquad 8T_1 = L_{11}+2L_{12}+L_{22}\\"
                        r"8R_0e^{4i\Phi_0} = L_{11}+4iL_{16}-2L_{12}-4L_{66}-4iL_{26}+L_{22}\\"
                        r"8R_1e^{2i\Phi_1} = L_{11}+2iL_{16}+2iL_{26}-L_{22}", 28, MUTED
                        ).to_edge(DOWN, buff=0.35)

        indices = tex(r"indices du cours : $L_{1111} = L_{11}$, $L_{1122} = L_{12}$, $L_{1212} = L_{66}$, "
                      r"$L_{1112} = L_{16}$, $L_{2212} = L_{26}$", 24, MUTED).next_to(formulas, UP, buff=0.2)

        with self.voice("T0, T1, R0 et R1 ne bougent pas quand on tourne les axes."):
            self.play(Create(inv), FadeIn(inv_lab), run_time=1.0)
            self.play(FadeIn(formulas), FadeIn(indices), run_time=0.8)
            self.wait(1.0)

        with self.voice("Et les symétries se lisent directement dessus."):
            self.play(FadeOut(VGroup(head, generic, table, *notes, inv, inv_lab, formulas, indices)),
                      run_time=0.8)

        # ----- polar diagram morphing (P2 slide 38) -----
        R0 = ValueTracker(PP_Q["R0"])
        R1 = ValueTracker(PP_Q["R1"])

        def params():
            return {"T0": PP_Q["T0"], "T1": PP_Q["T1"], "R0": R0.get_value(),
                    "R1": R1.get_value(), "Phi0": 0.0, "Phi1": 0.0}

        guide = VGroup(*[Circle(radius=r, color=MUTED, stroke_width=1, stroke_opacity=0.4).move_to(DIAG_C)
                         for r in (0.65, 1.3, 1.95, 2.6)])
        hline = DashedLine(DIAG_C + LEFT * 2.9, DIAG_C + RIGHT * 2.9, color=MUTED, stroke_width=1)
        vline = DashedLine(DIAG_C + DOWN * 2.9, DIAG_C + UP * 2.9, color=MUTED, stroke_width=1)
        curve = always_redraw(lambda: polar_curve(params(), DIAG_C, SCALE, COL_Q, stroke=5))
        lab_title = tex(r"Diagramme polaire : rigidité $L_{11}(\theta)$\\dans chaque direction $\theta$",
                        30, FG).move_to([3.4, 2.4, 0])

        def readout():
            return VGroup(
                VGroup(math("R_0 =", 36, FG),
                       DecimalNumber(R0.get_value(), num_decimal_places=0, font_size=36, color=FG, group_with_commas=False),
                       tex("MPa", 30, MUTED)).arrange(RIGHT, buff=0.15),
                VGroup(math("R_1 =", 36, FG),
                       DecimalNumber(R1.get_value(), num_decimal_places=0, font_size=36, color=FG, group_with_commas=False),
                       tex("MPa", 30, MUTED)).arrange(RIGHT, buff=0.15),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([3.4, 0.9, 0])

        values = always_redraw(readout)
        shape_lab = tex(r"le pli : un « 8 » allongé", 32, COL_Q).move_to([3.4, -0.8, 0])

        with self.voice("Sur le diagramme polaire, qui trace la rigidité dans chaque direction :"):
            self.play(FadeIn(guide), FadeIn(hline), FadeIn(vline), FadeIn(lab_title), run_time=0.6)
            self.play(Create(curve), FadeIn(values), FadeIn(shape_lab), run_time=1.8)

        def morph(r0, r1, label, color, text):
            new = tex(label, 32, color).move_to(shape_lab)
            with self.voice(text):
                self.play(R0.animate.set_value(r0), R1.animate.set_value(r1),
                          Transform(shape_lab, new), run_time=2.0)

        # Didactic values: R1 is reduced for the peanut so that L11 stays positive
        morph(0.0, 12000.0, r"$R_0 = 0$ : orthotropie $R_0$, « cacahuète »", COL_A,
              "R0 nul donne une cacahuète,")
        morph(PP_Q["R0"], 0.0, r"$R_1 = 0$ : symétrie du carré, 4 lobes", COL_D,
              "R1 nul donne quatre lobes,")
        morph(0.0, 0.0, r"$R_0 = R_1 = 0$ : isotropie, cercle", ACCENT,
              "et les deux nuls donnent un cercle, une plaque isotrope.")
