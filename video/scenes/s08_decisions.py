"""
Scene 8 - Two decisions of the group (scenario.md, about 0:45).

1. The cost of the slide 51 example: our value (slide 45 formula) and the
   slide value, exactly n^2 = 36 times larger (checked in
   tests/test_fitness.py). The value is recomputed here with fitness.cost.
2. "Orthotropie R1" read as R1(D*) = 0 (square symmetry, Phi9), pending the
   teacher's confirmation.
"""

from manim import (
    Create, Cross, FadeIn, FadeOut, GrowArrow, Arrow, LaggedStart, RoundedRectangle,
    VGroup, Write, Indicate,
)

from common import (
    ACCENT, COL_D, DOWN, FG, LEFT, MUTED, RIGHT, UP, NarratedScene, config, math,
    np, tex,
)

import fitness as fit  # project code, read-only
import laminate as lam

# T300/5208 ply of P2 slide 49 (same data as tests/test_mechanics.py)
T300 = dict(E1=181000.0, E2=10300.0, NU12=0.28, G12=7170.0)
SLIDE_51_STACK = [9, 0, 18, -4, 14, 5]
SLIDE_51_VALUE = 3.5873e-6


def our_value():
    Q = lam.ply_stiffness(lam.ply_compliance(T300["E1"], T300["E2"], T300["NU12"], T300["G12"]))
    return fit.cost(SLIDE_51_STACK, Q, config.T_PLY, [1, 3, 7, 11])


def sci(x):
    """3.5873e-06 -> '3{,}5873 \\times 10^{-6}'."""
    m, e = f"{x:.4e}".split("e")
    return rf"{m.replace('.', '{,}')} \times 10^{{{int(e)}}}"


def warning_box(width=12.4, height=5.6):
    return RoundedRectangle(width=width, height=height, corner_radius=0.2, color=ACCENT,
                            stroke_width=3, fill_color=ACCENT, fill_opacity=0.05)


class S08Decisions(NarratedScene):
    def construct(self):
        head = tex(r"Deux décisions du groupe", 46, ACCENT).to_edge(UP, buff=0.5)
        with self.voice("Deux points de l'énoncé nous ont obligés à trancher."):
            self.play(Write(head), run_time=1.2)

        # ----- 1. Phi1 and slide 51 -----
        box = warning_box().shift(DOWN * 0.4)
        t1 = tex(r"1. $\Phi_1$ et l'exemple de la slide 51", 34, ACCENT).move_to(box.get_top() + DOWN * 0.5)
        stack = math(r"[9/0/18/{-4}/14/5],\ \text{6 plis T300/5208}", 34, MUTED).next_to(t1, DOWN, buff=0.3)
        v = our_value()
        ours = tex(rf"notre formule (slide 45) : $\Phi = {sci(v)}$", 34, FG).next_to(stack, DOWN, buff=0.45)

        with self.voice("Le premier concerne Phi1. Sur l'exemple de la slide 51, notre formule "
                        "donne environ 10 puissance moins 7."):
            self.play(Create(box), FadeIn(t1), run_time=0.8)
            self.play(FadeIn(stack), run_time=0.6)
            self.play(Write(ours), run_time=1.4)

        theirs = tex(rf"valeur affichée sur la slide : $\Phi = {sci(SLIDE_51_VALUE)}$", 34, FG
                     ).next_to(ours, DOWN, buff=0.3)
        ratio = math(rf"\frac{{{sci(SLIDE_51_VALUE)}}}{{{sci(v)}}} = {f"{SLIDE_51_VALUE / v:.2f}".replace(".", "{,}")} = 6^2 = n^2",
                     38, ACCENT).next_to(theirs, DOWN, buff=0.4)
        with self.voice("La slide affiche une valeur exactement 36 fois plus grande, et 36, "
                        "c'est le nombre de plis au carré."):
            self.play(FadeIn(theirs), run_time=0.8)
            self.play(Write(ratio), run_time=1.6)

        keep = tex(r"$\Rightarrow$ on garde la formule de la slide 45 ;\\"
                   r"la valeur de la slide est traitée comme une erreur numérique", 30, FG
                   ).next_to(ratio, DOWN, buff=0.35)
        with self.voice("On garde la formule de la slide 45 et on considère la valeur de la "
                        "slide comme une erreur numérique."):
            self.play(FadeIn(keep, shift=0.2 * UP), run_time=1.0)

        # ----- 2. "orthotropie R1" -----
        box2 = warning_box().shift(DOWN * 0.4)
        t2 = tex(r"2. « orthotropie $R_1$ » en flexion", 34, ACCENT).move_to(box2.get_top() + DOWN * 0.5)
        quote = tex(r"« orthotropie $R_1$ »", 44, FG).move_to([-3.2, 0.4, 0])
        missing = tex(r"terme absent du cours", 28, MUTED).next_to(quote, DOWN, buff=0.3)
        cross = Cross(quote, stroke_color=COL_D, stroke_width=5).set_opacity(0.8)

        with self.voice("Le second : l'énoncé parle d'orthotropie R1 en flexion, un terme qui "
                        "n'existe pas dans le cours."):
            self.play(FadeOut(VGroup(box, t1, stack, ours, theirs, ratio, keep)), run_time=0.6)
            self.play(Create(box2), FadeIn(t2), run_time=0.8)
            self.play(FadeIn(quote), FadeIn(missing), run_time=0.8)
            self.play(Create(cross), run_time=0.6)

        reading = VGroup(
            math(r"R_1^{D^*} = 0", 46, COL_D),
            tex(r"symétrie du carré (slide 47)", 30, FG),
            math(r"\Rightarrow \Phi_9", 44, COL_D),
        ).arrange(DOWN, buff=0.3).move_to([3.0, 0.3, 0])
        arrow = Arrow(quote.get_right() + RIGHT * 0.2, reading.get_left() + LEFT * 0.2, buff=0.1,
                      color=FG, stroke_width=4)

        with self.voice("On l'a lu comme R1 de D étoile nul, ce que le cours appelle la "
                        "symétrie du carré."):
            self.play(GrowArrow(arrow), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(r) for r in reading], lag_ratio=0.4), run_time=1.6)

        confirm = tex(r"à confirmer avec le professeur \quad (une ligne de \texttt{config.py})",
                      30, ACCENT).move_to(box2.get_bottom() + UP * 0.6)
        with self.voice("On attend la confirmation du professeur ; si on s'est trompés, c'est "
                        "une ligne à changer dans le code."):
            self.play(FadeIn(confirm, shift=0.2 * UP), run_time=1.0)
