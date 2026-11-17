"""
Scene 3 - From S to Q (scenario.md, about 0:35).

Hooke's law in plane stress, the compliance S filled with the ply constants,
Q = S^-1 (numerical values from laminate.py), then the rotation formulas of
Q(delta) piling up until the screen is unreadable.
"""

from manim import (
    FadeIn, FadeOut, LaggedStart, ReplacementTransform, SurroundingRectangle,
    TransformMatchingTex, VGroup, Write, Create,
)

from common import (
    ACCENT, COL_Q, DOWN, FG, LEFT, MUTED, RIGHT, UP, NarratedScene, config,
    math, np, tex,
)

import laminate as lam  # project code, read-only

EPS = r"\begin{Bmatrix}\varepsilon_{11}\\ \varepsilon_{22}\\ \gamma_{12}\end{Bmatrix}"
SIG = r"\begin{Bmatrix}\sigma_{11}\\ \sigma_{22}\\ \sigma_{12}\end{Bmatrix}"

ROTATION = [
    r"\bar Q_{11} = Q_{11}c^4 + 2(Q_{12}+2Q_{66})s^2c^2 + Q_{22}s^4",
    r"\bar Q_{16} = (Q_{11}-Q_{12}-2Q_{66})\,sc^3 + (Q_{12}-Q_{22}+2Q_{66})\,s^3c",
    r"\bar Q_{22} = Q_{11}s^4 + 2(Q_{12}+2Q_{66})s^2c^2 + Q_{22}c^4",
    r"\bar Q_{12} = (Q_{11}+Q_{22}-4Q_{66})s^2c^2 + Q_{12}(s^4+c^4)",
    r"\bar Q_{66} = (Q_{11}+Q_{22}-2Q_{12}-2Q_{66})s^2c^2 + Q_{66}(s^4+c^4)",
    r"\bar Q_{26} = (Q_{11}-Q_{12}-2Q_{66})\,s^3c + (Q_{12}-Q_{22}+2Q_{66})\,sc^3",
]


class S03Stiffness(NarratedScene):
    def construct(self):
        title = tex(r"Loi de Hooke dans le plan du pli", 40, MUTED).to_edge(UP, buff=0.5)

        empty = math(EPS + r"=\begin{bmatrix}\ \cdot\ & \cdot & \cdot\ \\ \ \cdot\ & \cdot & \cdot\ \\ "
                     r"\ \cdot\ & \cdot & \cdot\ \end{bmatrix}" + SIG, 46)
        lab_def = tex("3 déformations", 26, MUTED).next_to(empty, DOWN, buff=0.4).align_to(empty, LEFT)
        lab_con = tex("3 contraintes", 26, MUTED).next_to(empty, DOWN, buff=0.4).align_to(empty, RIGHT)

        with self.voice("Pour décrire cette rigidité, on écrit la loi de Hooke dans le plan "
                        "de la plaque : trois déformations, trois contraintes, une matrice "
                        "3 par 3."):
            self.play(FadeIn(title), run_time=0.6)
            self.play(Write(empty), run_time=2.0)
            self.play(FadeIn(lab_def), FadeIn(lab_con), run_time=0.8)

        s_mat = math(EPS + r"=\underbrace{\begin{bmatrix}\dfrac{1}{E_1} & -\dfrac{\nu_{12}}{E_1} & 0\\[1.2ex]"
                     r"-\dfrac{\nu_{12}}{E_1} & \dfrac{1}{E_2} & 0\\[1.2ex] 0 & 0 & \dfrac{1}{G_{12}}"
                     r"\end{bmatrix}}_{\mathbf{S}}" + SIG, 44)
        def mpa(v):
            return f"{int(round(v)):,}".replace(",", r"\,")

        nu = f"{config.NU12}".replace(".", "{,}")
        consts = tex(rf"$E_1 = {mpa(config.E1)}$ MPa \quad $E_2 = {mpa(config.E2)}$ MPa \quad "
                     rf"$G_{{12}} = {mpa(config.G12)}$ MPa \quad $\nu_{{12}} = {nu}$",
                     26, MUTED).to_edge(DOWN, buff=0.6)

        with self.voice("La matrice de souplesse S se remplit directement avec les "
                        "constantes du pli."):
            self.play(FadeOut(lab_def, lab_con), run_time=0.3)
            self.play(ReplacementTransform(empty, s_mat), run_time=1.5)
            self.play(FadeIn(consts), run_time=0.6)

        Q = lam.ply_stiffness(lam.ply_compliance(config.E1, config.E2, config.NU12, config.G12))
        q_num = (r"\mathbf{Q} = \mathbf{S}^{-1} = \begin{bmatrix}"
                 + r"\\".join(" & ".join(f"{Q[i, j]:.0f}".replace("-0", "0") for j in range(3))
                              for i in range(3))
                 + r"\end{bmatrix}\ \text{MPa}")
        q_eq = math(q_num, 46, FG).shift(DOWN * 0.7 + RIGHT * 0.8)
        q_box = SurroundingRectangle(q_eq, color=COL_Q, buff=0.25)
        q_note = tex(r"rigidité réduite du pli, dans ses axes", 28, COL_Q).next_to(q_box, DOWN, buff=0.3)
        # Meaning of the Voigt indices 1, 2, 6 (explication_du_sujet, section 3.2)
        voigt = tex(r"$Q_{11}, Q_{22}$ : traction selon 1, 2 \quad $Q_{66}$ : cisaillement \quad "
                    r"$Q_{12}$ : effet Poisson\\$Q_{16} = Q_{26} = 0$ dans les axes du pli, "
                    r"non nuls dès qu'on tourne le pli", 26, MUTED).to_edge(DOWN, buff=0.35)

        with self.voice("On l'inverse, et on obtient Q, la rigidité du pli."):
            self.play(s_mat.animate.scale(0.55).to_corner(UP + LEFT, buff=0.4), FadeOut(title), run_time=0.8)
            self.play(Write(q_eq), run_time=1.2)
            self.play(Create(q_box), FadeIn(q_note), run_time=0.6)
            self.play(FadeOut(consts), FadeIn(voigt, shift=0.2 * UP), run_time=0.8)
            self.wait(1.5)

        rot_title = tex(r"Pli tourné de $\delta$ \quad ($c = \cos\delta$, $s = \sin\delta$)", 32, ACCENT)
        rot_title.to_edge(UP, buff=0.5)
        rows = VGroup(*[math(r, 34, FG) for r in ROTATION]).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        rows.next_to(rot_title, DOWN, buff=0.45)
        # Crowded copies to show how heavy the Cartesian route gets
        clutter = VGroup(*[
            math(ROTATION[i % 6], 30, MUTED).set_opacity(0.55)
            .move_to([np.sin(1.7 * i) * 2.5, np.cos(2.3 * i) * 2.6, 0]).rotate(0.08 * np.sin(i))
            for i in range(12)
        ])

        with self.voice("Pour un pli tourné de delta, il faut réécrire Q dans les axes de "
                        "la plaque, et les formules deviennent vite très lourdes."):
            self.play(FadeOut(s_mat, voigt, q_box, q_note), q_eq.animate.scale(0.5).to_corner(DOWN + RIGHT),
                      run_time=0.7)
            self.play(FadeIn(rot_title), run_time=0.4)
            self.play(LaggedStart(*[Write(r) for r in rows], lag_ratio=0.35), run_time=3.2)
            self.play(LaggedStart(*[FadeIn(c) for c in clutter], lag_ratio=0.1), run_time=1.4)

        polar = tex(r"$\rightarrow$ la méthode polaire", 56, ACCENT)
        with self.voice("C'est ce que la méthode polaire va simplifier."):
            self.play(FadeOut(VGroup(rows, clutter, rot_title, q_eq), scale=0.6), run_time=0.8)
            self.play(FadeIn(polar, scale=1.2), run_time=0.7)
