"""
Scene 11 - Ending (scenario.md, about 0:30).

The whole path in one row of small pictures (ply, A* B* D*, closing arrows,
GA loop, polar diagram), the remaining work, and the closing card.
"""

from manim import (
    Arrow, Circle, CurvedArrow, FadeIn, FadeOut, LaggedStart, Square, VGroup, Write,
    PI, Create,
)

from common import (
    ACCENT, COL_A, COL_B, COL_D, COL_Q, COL_RESIN, DOWN, FG, LEFT, MUTED, RIGHT, UP,
    NarratedScene, arrow_chain, config, fibre_hatch, math, np, polar_curve, tex,
)

import laminate as lam  # project code, read-only
import polar as pol

BEST = [22, -41, 80, -15, -89, 42, -61, 61, -74, 83,
        -72, -38, 67, -52, 43, 84, 5, 38, -25, -82]


class S11End(NarratedScene):
    def construct(self):
        xs = [-5.4, -2.7, 0.0, 2.7, 5.4]
        y = 0.8

        ply = VGroup(Square(1.4, stroke_width=0, fill_color=COL_RESIN, fill_opacity=0.85).move_to([xs[0], y, 0]),
                     fibre_hatch([xs[0], y], 1.4, 1.4, 30, spacing=0.13, stroke=2))
        mats = VGroup(math(r"\mathbf{A}^*", 40, COL_A), math(r"\mathbf{B}^*", 40, COL_B),
                      math(r"\mathbf{D}^*", 40, COL_D)).arrange(DOWN, buff=0.15).move_to([xs[1], y, 0])
        tri, _ = arrow_chain(np.radians([0, 240, 120]), None, origin=(0, 0, 0), scale=1.1,
                             colors=[COL_Q, ACCENT, COL_A], stroke=4)
        tri.move_to([xs[2], y, 0])
        loop = VGroup(CurvedArrow([xs[3] + 0.7, y, 0], [xs[3] - 0.7, y, 0], angle=PI, color=ACCENT),
                      CurvedArrow([xs[3] - 0.7, y, 0], [xs[3] + 0.7, y, 0], angle=PI, color=ACCENT),
                      tex("AG", 34, FG).move_to([xs[3], y, 0]))
        Q = lam.ply_stiffness(lam.ply_compliance(config.E1, config.E2, config.NU12, config.G12))
        _, _, D_s, _ = lam.laminate_matrices(Q, BEST, config.T_PLY)
        diag = polar_curve(pol.polar_parameters(D_s), [xs[4], y], 0.75 / 70000.0, COL_D, stroke=4)
        icons = [ply, mats, tri, loop, diag]
        caps = ["constantes du pli", "matrices du stratifié", "flèches à refermer",
                "recherche des 20 angles", "symétries obtenues"]
        captions = VGroup(*[tex(c, 24, MUTED).move_to([x, y - 1.25, 0]) for c, x in zip(caps, xs)])
        links = VGroup(*[Arrow([xs[i] + 0.85, y, 0], [xs[i + 1] - 0.85, y, 0], buff=0, color=MUTED,
                               stroke_width=3) for i in range(4)])

        with self.voice("On part donc des constantes d'un pli, on construit A étoile, B étoile et "
                        "D étoile, la méthode polaire transforme les symétries voulues en flèches "
                        "qui doivent se refermer, et l'algorithme génétique cherche les vingt angles "
                        "qui les referment."):
            for i, (ic, cap) in enumerate(zip(icons, captions)):
                anims = [FadeIn(ic, scale=0.8), FadeIn(cap)]
                if i:
                    anims.append(Create(links[i - 1]))
                self.play(*anims, run_time=1.0)
                self.wait(1.2)

        todo = VGroup(
            tex(r"$\square$ confirmer $\Phi_9$ avec le professeur", 32, FG),
            tex(r"$\square$ relancer avec d'autres graines", 32, FG),
            tex(r"$\square$ écrire le rapport", 32, FG),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([0, -2.4, 0])
        todo_t = tex("Il reste à :", 30, ACCENT).next_to(todo, LEFT, buff=0.6).align_to(todo, UP)

        with self.voice("Il nous reste à confirmer Phi9 avec le professeur, à relancer le calcul "
                        "avec d'autres graines pour vérifier que le résultat tient, et à écrire "
                        "le rapport."):
            self.play(VGroup(*icons, captions, links).animate.shift(UP * 1.2), run_time=0.6)
            self.play(FadeIn(todo_t), LaggedStart(*[FadeIn(t, shift=0.2 * RIGHT) for t in todo],
                                                  lag_ratio=0.6), run_time=2.4)

        card = VGroup(tex(r"Optimiser un stratifié par algorithme génétique", 44, FG),
                      tex(r"EVCSP, groupe 1", 32, MUTED),
                      tex(r"\texttt{github.com/EwanMCARTHY/AG\_montemurro}", 28, ACCENT)
                      ).arrange(DOWN, buff=0.35)
        self.play(FadeOut(VGroup(*icons, captions, links, todo, todo_t)), run_time=0.8)
        self.play(FadeIn(card), run_time=1.0)
        self.wait(3.0)
