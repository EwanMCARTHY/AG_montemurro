"""
Cost function (sum of partial objectives) and fitness of the GA.

Partial objectives: P2 slides 45-47. All of them are dimensionless and equal
to zero when the target elastic symmetry is reached, so the theoretical
minimum of the cost function is 0 (P2 slide 44).

Fitness: statement, section 2.a.
"""

import numpy as np

import laminate as lam
import polar as pol

# Partial objectives that use a polar angle (need R0 and R1 non-zero on the
# tensor involved), and those that set a modulus R0 or R1 to zero.
# Combining them on the same tensor is meaningless: when R0 or R1 is zero the
# corresponding polar angle is not defined (P2 slide 38).
_ANGLE_OBJECTIVES = {3: "A", 7: "D"}
_ZERO_MODULUS_OBJECTIVES = {4: "A", 5: "A", 6: "A", 8: "D", 9: "D", 10: "D"}


def check_objectives(objectives):
    """
    Raise an error if the list of objectives contains an incompatible
    combination (see the comment above). Phi11 uses Phi1 of A* and D*,
    so it is incompatible with any objective that cancels R1 (5, 6, 9, 10).
    """
    for obj in objectives:
        if obj not in range(1, 12):
            raise ValueError(f"Unknown partial objective Phi{obj}")
    for ang, tensor in _ANGLE_OBJECTIVES.items():
        for zero, tensor_zero in _ZERO_MODULUS_OBJECTIVES.items():
            if ang in objectives and zero in objectives and tensor == tensor_zero:
                raise ValueError(f"Phi{ang} and Phi{zero} cannot be combined: "
                                 f"the polar angles of {tensor}* are undefined")
    if 11 in objectives:
        for zero in (5, 6, 9, 10):
            if zero in objectives:
                raise ValueError(f"Phi11 and Phi{zero} cannot be combined: "
                                 "Phi1 is undefined when R1 = 0")


def wrap_angle(x, period):
    """
    Bring an angle into [-period/2, period/2).

    Phi0 is defined modulo pi/2 and Phi1 modulo pi, so Phi0 - Phi1 is only
    defined modulo pi/2: the distance to K pi/4 must be measured on this
    circle, otherwise a laminate at the target can look far from it.
    """
    return (x + period / 2.0) % period - period / 2.0


def partial_objectives(ppA, ppB, ppD, ppC, pp_ply, K_A=0, K_D=0):
    """
    The eleven partial objectives of P2 slides 45-47, as a dict {index: value}.

    ppA, ppB, ppD, ppC : polar parameters of A*, B*, D*, C = A* - D*
    pp_ply             : polar parameters of the ply stiffness Q
    K_A, K_D           : K = 0 or 1 for the ordinary orthotropy objectives
    """
    norm_Q = pol.polar_norm(pp_ply)
    R0, R1 = pp_ply["R0"], pp_ply["R1"]
    quarter_pi = np.pi / 4.0

    phi = {}
    # --- Slide 45 ---
    phi[1] = (pol.polar_norm(ppB) / norm_Q)**2            # decoupling B* = 0
    phi[2] = (pol.polar_norm(ppC) / norm_Q)**2            # homogeneity C = 0

    # --- Slide 46: membrane (A*) ---
    dA = wrap_angle(ppA["Phi0"] - ppA["Phi1"] - K_A * quarter_pi, np.pi / 2.0)
    phi[3] = (dA / quarter_pi)**2                          # ordinary orthotropy
    phi[4] = (ppA["R0"] / R0)**2                           # R0-orthotropy
    phi[5] = (ppA["R1"] / R1)**2                           # square symmetry
    phi[6] = (ppA["R0"]**2 + 4 * ppA["R1"]**2) / (R0**2 + 4 * R1**2)  # isotropy

    # --- Slide 47: bending (D*) ---
    dD = wrap_angle(ppD["Phi0"] - ppD["Phi1"] - K_D * quarter_pi, np.pi / 2.0)
    phi[7] = (dD / quarter_pi)**2                          # ordinary orthotropy
    phi[8] = (ppD["R0"] / R0)**2                           # R0-orthotropy
    phi[9] = (ppD["R1"] / R1)**2                           # square symmetry
    phi[10] = (ppD["R0"]**2 + 4 * ppD["R1"]**2) / (R0**2 + 4 * R1**2)  # isotropy

    # --- Slide 47: coincident membrane/bending orthotropy axes ---
    d1 = wrap_angle(ppA["Phi1"] - ppD["Phi1"], np.pi)     # Phi1 defined modulo pi
    phi[11] = (d1 / quarter_pi)**2
    return phi


def laminate_polar(Q, angles_deg, t_ply):
    """Polar parameters of A*, B*, D*, C of a stacking (Cartesian route)."""
    A_s, B_s, D_s, C = lam.laminate_matrices(Q, angles_deg, t_ply)
    return (pol.polar_parameters(A_s), pol.polar_parameters(B_s),
            pol.polar_parameters(D_s), pol.polar_parameters(C))


def cost(angles_deg, Q, t_ply, objectives, K_A=0, K_D=0):
    """
    Cost function Phi(delta) = sum of the selected partial objectives
    (P2 slide 44). Its theoretical minimum is 0.
    """
    pp_ply = pol.polar_parameters(Q)
    ppA, ppB, ppD, ppC = laminate_polar(Q, angles_deg, t_ply)
    phi = partial_objectives(ppA, ppB, ppD, ppC, pp_ply, K_A, K_D)
    return sum(phi[i] for i in objectives)


def fitness(costs, p=1.0):
    """
    Fitness of the N individuals (statement, section 2.a):

        f_i = (1 - (Phi_i - min Phi) / (max Phi - min Phi))^p

    The best individual (lowest cost) gets f = 1, the worst f = 0.
    If all costs are equal, every individual gets f = 1 (no preference).
    """
    costs = np.asarray(costs, dtype=float)
    c_min, c_max = costs.min(), costs.max()
    if c_max == c_min:
        return np.ones_like(costs)
    return (1.0 - (costs - c_min) / (c_max - c_min))**p
