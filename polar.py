"""
Polar method of G. Verchery (1979) for plane 4th-order elasticity tensors
(P2 slides 35-42).

A tensor L is described by
    T0, T1 : isotropic moduli
    R0, R1 : anisotropic moduli
    Phi0, Phi1 : polar angles
Only T0, T1, R0, R1 and the difference Phi0 - Phi1 are tensor invariants.

Polar parameters are returned as a dict with the keys
"T0", "T1", "R0", "R1", "Phi0", "Phi1" (angles in radians).
"""

import numpy as np


def polar_parameters(L):
    """
    Polar parameters of a 3x3 stiffness-like matrix L (inverse law, P2
    slide 36). With Voigt components:
        L1111 = L11, L1122 = L12, L1212 = L66,
        L1112 = L16, L2212 = L26, L2222 = L22

        8 T0             = L11 - 2 L12 + 4 L66 + L22
        8 T1             = L11 + 2 L12 + L22
        8 R0 e^(4i Phi0) = L11 + 4i L16 - 2 L12 - 4 L66 - 4i L26 + L22
        8 R1 e^(2i Phi1) = L11 + 2i L16 + 2i L26 - L22

    Phi0 and Phi1 are meaningless (numerical noise) when R0 or R1 is zero.
    """
    L11, L12, L16 = L[0, 0], L[0, 1], L[0, 2]
    L22, L26, L66 = L[1, 1], L[1, 2], L[2, 2]

    T0 = (L11 - 2 * L12 + 4 * L66 + L22) / 8.0
    T1 = (L11 + 2 * L12 + L22) / 8.0
    z0 = (L11 + 4j * L16 - 2 * L12 - 4 * L66 - 4j * L26 + L22) / 8.0
    z1 = (L11 + 2j * L16 + 2j * L26 - L22) / 8.0

    return {
        "T0": T0,
        "T1": T1,
        "R0": np.abs(z0),
        "R1": np.abs(z1),
        "Phi0": np.angle(z0) / 4.0,   # Phi0 in ]-pi/4, pi/4]
        "Phi1": np.angle(z1) / 2.0,   # Phi1 in ]-pi/2, pi/2]
    }


def stiffness_from_polar(pp, theta=0.0):
    """
    Cartesian components of a tensor from its polar parameters (P2 slide 35),
    in a frame rotated by theta [rad]. A rotation of the frame simply
    subtracts theta from the polar angles (P2 slide 37).

    Returns the 3x3 Voigt matrix.
    """
    T0, T1, R0, R1 = pp["T0"], pp["T1"], pp["R0"], pp["R1"]
    a0 = 4.0 * (pp["Phi0"] - theta)
    a1 = 2.0 * (pp["Phi1"] - theta)

    L11 = T0 + 2 * T1 + R0 * np.cos(a0) + 4 * R1 * np.cos(a1)
    L16 = R0 * np.sin(a0) + 2 * R1 * np.sin(a1)
    L12 = -T0 + 2 * T1 - R0 * np.cos(a0)
    L66 = T0 - R0 * np.cos(a0)
    L26 = -R0 * np.sin(a0) + 2 * R1 * np.sin(a1)
    L22 = T0 + 2 * T1 + R0 * np.cos(a0) - 4 * R1 * np.cos(a1)

    return np.array([
        [L11, L12, L16],
        [L12, L22, L26],
        [L16, L26, L66],
    ])


def polar_norm(pp):
    """
    Norm of a plane 4th-order elasticity tensor (P2 slide 45):
        ||L|| = sqrt(T0^2 + 2 T1^2 + R0^2 + 4 R1^2)
    """
    return np.sqrt(pp["T0"]**2 + 2 * pp["T1"]**2 + pp["R0"]**2 + 4 * pp["R1"]**2)


def _from_complex(T0, T1, z0, z1):
    """Build a polar-parameter dict from T0, T1 and the two complex numbers
    z0 = R0 e^(4i Phi0) and z1 = R1 e^(2i Phi1)."""
    return {
        "T0": T0,
        "T1": T1,
        "R0": np.abs(z0),
        "R1": np.abs(z1),
        "Phi0": np.angle(z0) / 4.0,
        "Phi1": np.angle(z1) / 2.0,
    }


def laminate_polar_direct(ply_pp, angles_deg):
    """
    Polar parameters of A*, B*, D* and C computed directly from those of the
    ply, without any Cartesian matrix (P2 slides 41-42):

        A*: T0, T1 of the ply,
            R0 e^(4i Phi0) = (1/n)   R0 e^(4i Phi0_ply) sum_k       e^(4i delta_k)
            R1 e^(2i Phi1) = (1/n)   R1 e^(2i Phi1_ply) sum_k       e^(2i delta_k)
        B*: T0 = T1 = 0,
            same with (1/n^2) sum_k b_k e^(...)
        D*: T0, T1 of the ply,
            same with (1/n^3) sum_k d_k e^(...)
        C = A* - D*: T0 = T1 = 0, difference of the complex numbers

    The coefficients b_k and d_k follow from B* = 2B/h^2 and D* = 12D/h^3
    with h = n t and the interfaces z_k of laminate.ply_interfaces:
        b_k = (z_k^2 - z_{k-1}^2) / t^2
        d_k = 4 (z_k^3 - z_{k-1}^3) / t^3
    In integer form (z_k / t = k - n/2): b_k = 2k - n - 1,
    d_k = 12 k (k - n - 1) + 4 + 3 n (n + 2).

    Used as an independent cross-check of the Cartesian route.
    """
    delta = np.radians(np.atleast_1d(angles_deg).astype(float))
    n = delta.size

    # Dimensionless interface coordinates z_k / t, k = 0..n
    zt = -n / 2.0 + np.arange(n + 1)
    b = zt[1:]**2 - zt[:-1]**2
    d = 4.0 * (zt[1:]**3 - zt[:-1]**3)

    e4 = np.exp(4j * delta)
    e2 = np.exp(2j * delta)

    # Complex polar moduli of the ply: R0 e^(4i Phi0), R1 e^(2i Phi1)
    z0_ply = ply_pp["R0"] * np.exp(4j * ply_pp["Phi0"])
    z1_ply = ply_pp["R1"] * np.exp(2j * ply_pp["Phi1"])

    zA0 = z0_ply * np.sum(e4) / n
    zA1 = z1_ply * np.sum(e2) / n
    zB0 = z0_ply * np.sum(b * e4) / n**2
    zB1 = z1_ply * np.sum(b * e2) / n**2
    zD0 = z0_ply * np.sum(d * e4) / n**3
    zD1 = z1_ply * np.sum(d * e2) / n**3

    T0, T1 = ply_pp["T0"], ply_pp["T1"]
    return {
        "A": _from_complex(T0, T1, zA0, zA1),
        "B": _from_complex(0.0, 0.0, zB0, zB1),
        "D": _from_complex(T0, T1, zD0, zD1),
        "C": _from_complex(0.0, 0.0, zA0 - zD0, zA1 - zD1),
    }
