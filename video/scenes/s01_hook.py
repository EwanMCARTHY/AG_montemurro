"""
Scene 1 - Hook (scenario.md, about 0:30).

A 20-ply laminate appears ply by ply, the ply angles spin like a slot
machine, the size of the design space is written (180^20), then the angles
settle on the best stacking found by the GA (seed 1) and the title appears.
"""

from manim import (
    DecimalNumber, FadeIn, FadeOut, Group, LaggedStart, Rectangle, SurroundingRectangle,
    VGroup, Write, Create, ORIGIN,
)

from common import (
    ACCENT, COL_RESIN, DOWN, FG, LEFT, MUTED, RIGHT, UP, NarratedScene,
    fibre_hatch, math, np, tex,
)

N_PLIES = 20
STRIP_W, STRIP_H, GAP = 5.0, 0.19, 0.045
STACK_X = -2.6

# Best stacking of the full run (results/best_laminate.txt, seed 1), ply 1 first
BEST = [22, -41, 80, -15, -89, 42, -61, 61, -74, 83,
        -72, -38, 67, -52, 43, 84, 5, 38, -25, -82]


def ply_center(k):
    """Centre of ply k (0 = bottom ply)."""
    y0 = -(N_PLIES * (STRIP_H + GAP) - GAP) / 2 + STRIP_H / 2
    return np.array([STACK_X, y0 + k * (STRIP_H + GAP), 0.0])


def hatches(angles):
    return VGroup(*[
        fibre_hatch(ply_center(k), STRIP_W, STRIP_H, a, spacing=0.11, stroke=1.3)
        for k, a in enumerate(angles)
    ])


class S01Hook(NarratedScene):
    def construct(self):
        rng = np.random.default_rng(7)

        strips = VGroup(*[
            Rectangle(width=STRIP_W, height=STRIP_H, stroke_width=0,
                      fill_color=COL_RESIN, fill_opacity=0.9 if k % 2 else 0.75)
            .move_to(ply_center(k))
            for k in range(N_PLIES)
        ])
        angles = rng.integers(-89, 91, N_PLIES)
        fibres = hatches(angles)
        plies = VGroup(*[VGroup(s, f) for s, f in zip(strips, fibres)])

        labels = VGroup(*[
            DecimalNumber(a, num_decimal_places=0, unit=r"^\circ", font_size=22,
                          color=FG, include_sign=False)
            .next_to(ply_center(k) + RIGHT * STRIP_W / 2, RIGHT, buff=0.25)
            for k, a in enumerate(angles)
        ])
        bottom = tex(r"pli 1", 24, MUTED).next_to(strips[0], LEFT, buff=0.25)
        top = tex(r"pli 20", 24, MUTED).next_to(strips[-1], LEFT, buff=0.25)

        def spin(rounds, pause):
            """Slot-machine effect: redraw random fibre angles several times."""
            nonlocal fibres
            for _ in range(rounds):
                new_angles = rng.integers(-89, 91, N_PLIES)
                new_fibres = hatches(new_angles)
                self.remove(fibres)
                self.add(new_fibres)
                fibres = new_fibres
                for lab, a in zip(labels, new_angles):
                    lab.set_value(a)
                self.wait(pause)

        # --- Beat 1: the plate ---
        with self.voice("Une plaque de vingt couches de fibres de carbone."):
            self.play(LaggedStart(*[FadeIn(p, shift=0.15 * UP) for p in plies],
                                  lag_ratio=0.12), run_time=3)
            self.play(FadeIn(bottom), FadeIn(top), run_time=0.5)

        # --- Beat 2: 180 orientations per ply ---
        per_ply = tex(r"180 orientations possibles\\par pli", 34, FG).move_to([3.9, 1.6, 0])
        with self.voice("Pour chaque couche, on choisit une orientation parmi 180."):
            self.play(LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.05),
                      FadeIn(per_ply), run_time=1.5)
            spin(6, 0.3)

        # --- Beat 3: size of the design space ---
        count = math(r"180^{20} \approx 1{,}3\times 10^{45}", 52, ACCENT).move_to([3.9, 0.2, 0])
        caption = tex(r"empilements possibles", 30, MUTED).next_to(count, DOWN, buff=0.3)
        with self.voice("Ça fait 180 puissance 20 empilements possibles, à peu près "
                        "10 puissance 45. On ne peut pas tous les essayer."):
            self.play(Write(count), run_time=1.5)
            self.play(FadeIn(caption), run_time=0.5)
            spin(14, 0.18)

        # --- Beat 4: one specific stacking ---
        target = tex(r"On en cherche \emph{un}, qui donne\\à la plaque un comportement précis.",
                     30, FG).move_to([3.9, -1.9, 0])
        with self.voice("Pourtant, dans ce projet, on en cherche un qui donne à la "
                        "plaque un comportement bien précis."):
            spin(4, 0.3)
            best = hatches(BEST)
            self.remove(fibres)
            self.add(best)
            fibres = best
            for lab, a in zip(labels, BEST):
                lab.set_value(a)
            frame = SurroundingRectangle(VGroup(strips, labels), color=ACCENT, buff=0.15)
            self.play(Create(frame), FadeIn(target), run_time=1.2)

        # --- Beat 5: title ---
        title = tex(r"Optimiser un stratifié\\par algorithme génétique", 60, FG)
        subtitle = tex(r"Méthode polaire et symétries élastiques \quad EVCSP, groupe 1",
                       30, MUTED).next_to(title, DOWN, buff=0.5)
        # Every mobject on screen, including the plies added as (strip, fibres)
        # pairs at the start, so that no hatch is left behind.
        everything = Group(*self.mobjects)
        with self.voice("On va voir ce qu'on cherche, comment on le mesure, et comment "
                        "un algorithme génétique le trouve."):
            self.play(FadeOut(everything, shift=0.3 * DOWN), run_time=1)
            self.play(Write(title), run_time=1.5)
            self.play(FadeIn(subtitle, shift=0.2 * UP), run_time=0.8)
