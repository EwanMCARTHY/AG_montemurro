"""
Scene 9 - The genetic algorithm (scenario.md, about 1:25).

Vocabulary, 8-bit coding and the 76 invalid codes (modulo vs rejection),
then the loop of ga.run_ga step by step: initial population, cost and
fitness, roulette selection, one-point crossover, mutation, elitism.
Numbers come from config.py and from ga.py (BITS_PER_GENE, N_VALID_CODES).
"""

from manim import (
    AnnularSector, Arrow, Create, CurvedArrow, FadeIn, FadeOut, Flash, GrowArrow,
    Indicate, LaggedStart, Rectangle, Rotate, RoundedRectangle, Square,
    SurroundingRectangle, Transform, VGroup, Write, PI, TAU, ReplacementTransform,
    Circumscribe,
)

from common import (
    ACCENT, COL_A, COL_B, COL_D, COL_Q, DOWN, FG, LEFT, MUTED, RIGHT, UP,
    NarratedScene, config, math, np, tex,
)

import ga  # project code, read-only

GREEN, GREY = COL_A, "#4a5160"


def bits_row(bits, size=34, color=FG, buff=0.08):
    return VGroup(*[tex(r"\texttt{" + b + "}", size, color) for b in bits]).arrange(RIGHT, buff=buff)


class S09GA(NarratedScene):
    def construct(self):
        # ----- vocabulary -----
        pairs = [("individu", "un stratifié (20 angles)"), ("gène", "un angle de pli"),
                 ("génotype", r"les $20 \times 8 = 160$ bits"), ("adaptation", r"la fitness, tirée du coût $\Phi$")]
        voc = VGroup(*[
            VGroup(tex(a, 34, ACCENT), tex(r"$\rightarrow$ " + b, 34, FG)).arrange(RIGHT, buff=0.4)
            for a, b in pairs
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([0, 0.2, 0])
        head = tex(r"Un algorithme génétique imite l'évolution", 40, FG).to_edge(UP, buff=0.5)

        with self.voice("Un algorithme génétique imite l'évolution. Chaque individu est un "
                        "stratifié, chaque gène est un angle de pli."):
            self.play(FadeIn(head), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(r, shift=0.2 * RIGHT) for r in voc], lag_ratio=0.4),
                      run_time=2.4)

        # ----- 8-bit coding of one angle -----
        angle = 22
        code = angle - ga.ANGLE_MIN                     # 111
        bits = format(code, f"0{ga.BITS_PER_GENE}b")
        enc = VGroup(math(rf"\delta = {angle}^\circ", 44, FG),
                     math(r"\rightarrow", 44, MUTED),
                     math(rf"\text{{code}} = {code}", 44, FG),
                     math(r"\rightarrow", 44, MUTED),
                     bits_row(bits, 44, ACCENT)).arrange(RIGHT, buff=0.35).move_to([0, 1.6, 0])
        enc_note = tex(r"8 bits par angle", 30, MUTED).next_to(enc, DOWN, buff=0.3)

        with self.voice("Chaque angle est codé sur 8 bits."):
            self.play(FadeOut(VGroup(head, voc)), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(e) for e in enc], lag_ratio=0.3), FadeIn(enc_note),
                      run_time=1.6)

        ineq = math(r"2^7 = 128 \;<\; 180 \;\le\; 256 = 2^8", 48, FG).move_to([0, 0.0, 0])
        with self.voice("Sept bits ne donnent que 128 valeurs, pas assez pour 180 angles ; "
                        "huit en donnent 256."):
            self.play(Write(ineq), run_time=2.0)

        # band of the 256 codes
        cw = 12.0 / 256
        band = VGroup(*[
            Rectangle(width=cw, height=0.5, stroke_width=0,
                      fill_color=GREEN if k < ga.N_VALID_CODES else GREY, fill_opacity=1)
            .move_to([-6 + cw * (k + 0.5), -1.4, 0]) for k in range(256)
        ])
        lab_ok = tex(r"codes 0 à 179 : un angle chacun", 28, GREEN).next_to(band[90], DOWN, buff=0.25)
        lab_bad = tex(r"76 codes sans angle", 28, MUTED).next_to(band[218], DOWN, buff=0.25)

        with self.voice("Il reste donc 76 codes qui ne correspondent à aucun angle."):
            self.play(LaggedStart(*[FadeIn(b) for b in band], lag_ratio=0.004), run_time=1.6)
            self.play(FadeIn(lab_ok), FadeIn(lab_bad), run_time=0.6)

        # modulo: angles of codes 0..75 appear twice as often
        def histogram(heights, color, y0=-3.6, scale=0.5):
            w = 12.0 / 180
            return VGroup(*[
                Rectangle(width=w, height=scale * h, stroke_width=0, fill_color=color, fill_opacity=0.9)
                .move_to([-6 + w * (k + 0.5), y0 + scale * h / 2, 0]) for k, h in enumerate(heights)
            ])

        h_mod = np.ones(180)
        h_mod[:256 - 180] = 2
        hist_mod = histogram(h_mod, COL_D)
        mod_lab = tex(r"modulo : 76 angles tirés \textbf{deux fois} plus souvent", 30, COL_D
                      ).move_to([0, -1.6, 0])

        with self.voice("Avec un modulo, 76 angles auraient eu deux codes et seraient sortis "
                        "deux fois plus souvent."):
            self.play(FadeOut(VGroup(enc, enc_note, ineq)), VGroup(band, lab_ok, lab_bad).animate.shift(UP * 2.8),
                      run_time=0.8)
            self.play(FadeIn(hist_mod, shift=0.2 * UP), FadeIn(mod_lab), run_time=1.2)

        hist_rej = histogram(np.ones(180), GREEN)
        rej_lab = tex(r"rejet : code interdit $\Rightarrow$ l'enfant garde le gène du parent ; "
                      r"tous les angles à égalité", 28, GREEN).move_to(mod_lab)
        formula = math(r"\delta = -89^\circ + \text{code}", 40, FG).move_to([0, 0.2, 0])

        with self.voice("On a choisi le rejet : si un enfant reçoit un code interdit, il garde "
                        "le gène de son parent."):
            self.play(Transform(hist_mod, hist_rej), Transform(mod_lab, rej_lab), run_time=1.2)
            self.play(Write(formula), run_time=1.0)

        # ----- the loop -----
        steps = [
            rf"Population initiale ($N = {config.POP_SIZE}$)",
            r"Coût $\Phi$ de chaque individu",
            r"Fitness $f_i \in [0, 1]$",
            r"Sélection : roulette",
            rf"Croisement ($p_c = {config.P_CROSSOVER}$)".replace(".", "{,}"),
            r"Mutation ($p_m = 1/N$)",
            r"Rejet des codes invalides",
            r"Élitisme",
        ]
        boxes = VGroup()
        for s in steps:
            t = tex(s, 24, FG)
            b = RoundedRectangle(width=4.0, height=0.55, corner_radius=0.12, color=MUTED, stroke_width=2)
            boxes.add(VGroup(b, t.move_to(b)))
        boxes.arrange(DOWN, buff=0.22).to_edge(LEFT, buff=0.4)
        links = VGroup(*[Arrow(boxes[i].get_bottom(), boxes[i + 1].get_top(), buff=0.02, color=MUTED,
                               stroke_width=2, max_tip_length_to_length_ratio=0.5)
                         for i in range(len(boxes) - 1)])
        back = CurvedArrow(boxes[-1].get_right() + RIGHT * 0.05, boxes[1].get_right() + RIGHT * 0.05,
                           angle=PI / 2, color=ACCENT, stroke_width=3)
        stage_x = 2.4          # centre of the right-hand area for the mini-animations

        def focus(i):
            """Highlight step i of the loop."""
            return [boxes[j][0].animate.set_color(ACCENT if j == i else MUTED) for j in range(len(boxes))]

        rng = np.random.default_rng(5)
        dots = VGroup(*[Square(0.16, stroke_width=0, fill_color=COL_Q, fill_opacity=0.9)
                        .move_to([stage_x - 3 + 0.3 * (k % 20), 1.5 - 0.3 * (k // 20), 0]) for k in range(100)])
        pop_lab = tex(r"500 stratifiés tirés au hasard (100 montrés)", 28, MUTED).next_to(dots, DOWN, buff=0.3)

        with self.voice("La boucle part de 500 stratifiés tirés au hasard."):
            self.play(FadeOut(VGroup(band, lab_ok, lab_bad, hist_mod, mod_lab, formula)), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(b) for b in boxes], lag_ratio=0.1), Create(links), run_time=1.4)
            self.play(*focus(0), LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.01),
                      FadeIn(pop_lab), run_time=1.2)

        # cost and fitness on a 3-individual example (explication_du_sujet, sec. 6.3)
        ex_costs = [0.01, 0.05, 0.11]
        ex_fit = [1.0, 0.6, 0.0]
        rows = VGroup(*[
            VGroup(tex(f"individu {i + 1}", 30, FG),
                   math(rf"\Phi = {str(c).replace('.', '{,}')}", 34, FG),
                   math(r"\rightarrow", 34, MUTED),
                   math(rf"f = {str(f).replace('.0', '').replace('.', '{,}')}", 34, ACCENT))
            .arrange(RIGHT, buff=0.35) for i, (c, f) in enumerate(zip(ex_costs, ex_fit))
        ]).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([stage_x, 0.6, 0])
        fit_formula = math(r"f_i = 1 - \frac{\Phi_i - \min \Phi}{\max \Phi - \min \Phi}", 36, FG
                           ).next_to(rows, DOWN, buff=0.5)

        with self.voice("On calcule le coût de chacun, puis sa fitness : 1 pour le meilleur, "
                        "0 pour le pire."):
            self.play(FadeOut(VGroup(dots, pop_lab)), *focus(1), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(r[:2]) for r in rows], lag_ratio=0.3), run_time=1.0)
            self.play(*focus(2), LaggedStart(*[FadeIn(r[2:]) for r in rows], lag_ratio=0.3),
                      FadeIn(fit_formula), run_time=1.4)

        # roulette: shares 1/1.6 = 62.5 % and 0.6/1.6 = 37.5 %
        wc = np.array([stage_x, 0.2, 0])
        s1 = AnnularSector(inner_radius=0, outer_radius=1.6, angle=TAU * 0.625, start_angle=PI / 2,
                           color=COL_A, fill_opacity=0.85).move_arc_center_to(wc)
        s2 = AnnularSector(inner_radius=0, outer_radius=1.6, angle=TAU * 0.375,
                           start_angle=PI / 2 + TAU * 0.625, color=COL_Q, fill_opacity=0.85
                           ).move_arc_center_to(wc)
        l1 = tex(r"62,5 \%", 28, FG).move_to(wc + 0.9 * np.array([np.cos(PI / 2 + PI * 0.625), np.sin(PI / 2 + PI * 0.625), 0]))
        l2 = tex(r"37,5 \%", 28, FG).move_to(wc + 0.9 * np.array([np.cos(PI / 2 + TAU * 0.625 + PI * 0.375),
                                                                 np.sin(PI / 2 + TAU * 0.625 + PI * 0.375), 0]))
        wheel = VGroup(s1, s2, l1, l2)
        pointer = Arrow(wc + UP * 2.4, wc + UP * 1.6, buff=0, color=ACCENT, stroke_width=6)
        wheel_lab = tex(r"part de roue $\propto f_i$ ; on tourne 500 fois", 28, MUTED
                        ).next_to(wheel, DOWN, buff=0.4)

        with self.voice("À la sélection, chaque individu reçoit une part de roulette "
                        "proportionnelle à sa fitness, et on tourne la roue 500 fois pour "
                        "choisir les parents."):
            self.play(FadeOut(VGroup(rows, fit_formula)), *focus(3), run_time=0.5)
            self.play(FadeIn(wheel), GrowArrow(pointer), FadeIn(wheel_lab), run_time=1.0)
            self.play(Rotate(wheel, angle=3.4 * TAU, about_point=wc), run_time=3.0)

        # one-point crossover
        p1 = (bits_row("10110", 40, COL_A), bits_row("010", 40, COL_A))
        p2 = (bits_row("01100", 40, COL_Q), bits_row("111", 40, COL_Q))
        r1 = VGroup(tex("parent 1", 28, MUTED), p1[0], tex(r"$|$", 40, ACCENT), p1[1]).arrange(RIGHT, buff=0.2)
        r2 = VGroup(tex("parent 2", 28, MUTED), p2[0], tex(r"$|$", 40, ACCENT), p2[1]).arrange(RIGHT, buff=0.2)
        cross = VGroup(r1, r2).arrange(DOWN, buff=0.5).move_to([stage_x, 0.8, 0])
        cr_lab = tex(r"85 \% des paires : on coupe au même endroit\\et on échange les fins", 28, MUTED
                     ).next_to(cross, DOWN, buff=0.5)

        with self.voice("Les parents vont par deux : dans 85 % des cas, on coupe leurs bits au "
                        "même endroit et on échange les fins."):
            self.play(FadeOut(VGroup(wheel, pointer, wheel_lab)), *focus(4), run_time=0.5)
            self.play(FadeIn(cross), FadeIn(cr_lab), run_time=0.8)
            t1, t2 = p1[1].get_center(), p2[1].get_center()
            self.play(p1[1].animate.move_to(t2), p2[1].animate.move_to(t1), run_time=1.4)
            self.play(r1[0].animate.become(tex("enfant 1", 28, ACCENT).move_to(r1[0])),
                      r2[0].animate.become(tex("enfant 2", 28, ACCENT).move_to(r2[0])), run_time=0.6)

        # mutation: one bit flips
        gene = bits_row(bits, 48, FG, buff=0.12).move_to([stage_x, 0.6, 0])
        flip = 5
        new_bit = tex(r"\texttt{" + ("0" if bits[flip] == "1" else "1") + "}", 48, COL_D).move_to(gene[flip])
        mut_lab = tex(r"chaque gène : une chance sur 500\\qu'un de ses bits s'inverse", 28, MUTED
                      ).next_to(gene, DOWN, buff=0.6)

        with self.voice("Puis la mutation : chaque gène a une chance sur 500 de voir un de ses "
                        "bits inversé, ce qui garde de la diversité."):
            self.play(FadeOut(VGroup(cross, cr_lab)), *focus(5), run_time=0.5)
            self.play(FadeIn(gene), FadeIn(mut_lab), run_time=0.6)
            self.play(Indicate(gene[flip], color=COL_D, scale_factor=1.6), run_time=0.8)
            self.play(Transform(gene[flip], new_bit), Flash(gene[flip], color=COL_D), run_time=0.6)

        # elitism: the best parent replaces the worst child
        kids = VGroup(*[Square(0.45, stroke_width=0, fill_color=COL_Q, fill_opacity=0.8) for _ in range(8)]
                      ).arrange(RIGHT, buff=0.15).move_to([stage_x, 0.0, 0])
        kids[5].set_fill(COL_D, 0.9)
        worst = tex("pire enfant", 26, COL_D).next_to(kids[5], DOWN, buff=0.25)
        best = Square(0.45, stroke_width=0, fill_color=ACCENT, fill_opacity=1).move_to([stage_x, 1.8, 0])
        best_lab = tex("meilleur de la génération précédente", 26, ACCENT).next_to(best, UP, buff=0.2)
        el_lab = tex(r"la meilleure solution n'est jamais perdue", 30, FG).move_to([stage_x, -1.6, 0])

        with self.voice("Enfin, le meilleur individu de la génération précédente remplace le "
                        "pire enfant. On ne perd donc jamais la meilleure solution."):
            self.play(FadeOut(VGroup(gene, mut_lab)), *focus(7), run_time=0.5)
            self.play(FadeIn(kids), FadeIn(worst), FadeIn(best), FadeIn(best_lab), run_time=0.8)
            self.play(best.animate.move_to(kids[5]), FadeOut(kids[5]), FadeOut(worst), run_time=1.2)
            self.play(FadeIn(el_lab), run_time=0.6)

        params = tex(rf"$N = {config.POP_SIZE}$ \quad $N_{{gen}} = {config.N_GENERATIONS}$ \quad "
                     rf"$p_c = 0{{,}}85$ \quad $p_m = 1/N$ \quad $p = 1$", 30, FG).move_to([stage_x, -2.8, 0])
        with self.voice("Et on recommence, 500 fois."):
            self.play(*focus(1), Create(back), FadeIn(params), run_time=1.4)
