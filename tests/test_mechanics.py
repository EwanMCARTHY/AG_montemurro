"""
Checks of the ply and laminate mechanics against the course values.

Reference data (course P2):
- slide 49: polar parameters of the T300/5208 ply (rounded to 1 MPa);
- slide 51: polar parameters of A*, B*, D* for the 6-ply laminate
  [9/0/18/-4/14/5] made of T300/5208 plies, t = 0.125 mm.
"""

import numpy as np
import pytest

import laminate as lam
import polar as pol

T_PLY = 0.125
SLIDE_51_STACK = [9, 0, 18, -4, 14, 5]


@pytest.fixture
def q_t300():
    """Reduced stiffness of the T300/5208 ply (P2 slide 49)."""
    S = lam.ply_compliance(E1=181000.0, E2=10300.0, nu12=0.28, G12=7170.0)
    return lam.ply_stiffness(S)


def test_compliance_is_inverse_of_stiffness(q_t300):
    S = lam.ply_compliance(181000.0, 10300.0, 0.28, 7170.0)
    assert np.allclose(S @ q_t300, np.eye(3))


def test_t300_ply_polar_parameters(q_t300):
    """P2 slide 49: T0 = 26880, T1 = 24744, R0 = 19710, R1 = 21433 MPa,
    Phi0 = Phi1 = 0 (values rounded to 1 MPa on the slide)."""
    pp = pol.polar_parameters(q_t300)
    assert pp["T0"] == pytest.approx(26880.0, abs=0.5)
    assert pp["T1"] == pytest.approx(24744.0, abs=0.5)
    assert pp["R0"] == pytest.approx(19710.0, abs=0.5)
    assert pp["R1"] == pytest.approx(21433.0, abs=0.5)
    assert pp["Phi0"] == pytest.approx(0.0, abs=1e-12)
    assert pp["Phi1"] == pytest.approx(0.0, abs=1e-12)


def test_rotation_adds_angle_to_polar_angles(q_t300):
    """P2 slide 37: rotating the ply by delta shifts its polar angles by
    delta and leaves the moduli unchanged."""
    pp0 = pol.polar_parameters(q_t300)
    pp = pol.polar_parameters(lam.rotate_stiffness(q_t300, 20.0)[0])
    for key in ("T0", "T1", "R0", "R1"):
        assert pp[key] == pytest.approx(pp0[key], rel=1e-12)
    assert np.degrees(pp["Phi0"]) == pytest.approx(20.0, abs=1e-9)
    assert np.degrees(pp["Phi1"]) == pytest.approx(20.0, abs=1e-9)


def test_polar_round_trip(q_t300):
    """Cartesian -> polar -> Cartesian gives back the matrix (slides 35-36)."""
    Qr = lam.rotate_stiffness(q_t300, 33.0)[0]
    back = pol.stiffness_from_polar(pol.polar_parameters(Qr))
    assert np.allclose(back, Qr, rtol=1e-12, atol=1e-8)


def test_slide_51_laminate(q_t300):
    """P2 slide 51: polar parameters of A*, B*, D* for [9/0/18/-4/14/5]."""
    A_s, B_s, D_s, _ = lam.laminate_matrices(q_t300, SLIDE_51_STACK, T_PLY)
    ppA = pol.polar_parameters(A_s)
    ppB = pol.polar_parameters(B_s)
    ppD = pol.polar_parameters(D_s)

    # Values given with 4 decimals on the slide
    tol = 1e-4
    assert ppA["T0"] == pytest.approx(26880.4311, abs=tol)
    assert ppA["T1"] == pytest.approx(24743.8933, abs=tol)
    assert ppA["R0"] == pytest.approx(17033.4619, abs=tol)
    assert ppA["R1"] == pytest.approx(20683.2749, abs=tol)
    assert ppD["T0"] == pytest.approx(26880.4311, abs=tol)
    assert ppD["T1"] == pytest.approx(24743.8933, abs=tol)
    assert ppD["R0"] == pytest.approx(18772.4089, abs=tol)
    assert ppD["R1"] == pytest.approx(21173.5205, abs=tol)
    assert ppB["T0"] == pytest.approx(0.0, abs=1e-8)
    assert ppB["T1"] == pytest.approx(0.0, abs=1e-8)
    assert ppB["R0"] == pytest.approx(19.5909, abs=tol)
    assert ppB["R1"] == pytest.approx(2.83, abs=0.005)   # 2 decimals on the slide

    # Polar angles given as whole degrees on the slide
    for pp in (ppA, ppD):
        assert np.degrees(pp["Phi0"]) == pytest.approx(7.0, abs=0.5)
        assert np.degrees(pp["Phi1"]) == pytest.approx(7.0, abs=0.5)


@pytest.mark.parametrize("seed", range(5))
def test_cartesian_vs_direct_polar_sums(q_t300, seed):
    """Cross-check: the polar parameters of A*, B*, D*, C computed from the
    Cartesian matrices must equal those given by the direct sums in
    exp(4i delta_k) and exp(2i delta_k) (P2 slides 41-42)."""
    rng = np.random.default_rng(seed)
    n = rng.integers(2, 30)
    angles = rng.integers(-89, 91, size=n)

    matrices = dict(zip("ABDC", lam.laminate_matrices(q_t300, angles, T_PLY)))
    direct = pol.laminate_polar_direct(pol.polar_parameters(q_t300), angles)

    for name in "ABDC":
        cart = pol.polar_parameters(matrices[name])
        ref = direct[name]
        for key in ("T0", "T1", "R0", "R1"):
            assert cart[key] == pytest.approx(ref[key], rel=1e-9, abs=1e-7)
        # Compare the complex numbers R e^(i m Phi) rather than the angles,
        # which are undefined when R is close to zero
        for R, Phi, m in (("R0", "Phi0", 4), ("R1", "Phi1", 2)):
            zc = cart[R] * np.exp(1j * m * cart[Phi])
            zr = ref[R] * np.exp(1j * m * ref[Phi])
            assert abs(zc - zr) <= 1e-9 * max(1.0, abs(zr)) + 1e-7


def test_symmetric_laminate_is_decoupled(q_t300):
    """A mirror-symmetric stacking has B = 0."""
    _, B_s, _, _ = lam.laminate_matrices(q_t300, [30, -45, 0, 0, -45, 30], T_PLY)
    assert np.allclose(B_s, 0.0, atol=1e-9)


def test_isotropic_moduli_unchanged(q_t300):
    """P2 slides 41-42: T0, T1 of A* and D* equal those of the ply."""
    pp_ply = pol.polar_parameters(q_t300)
    A_s, _, D_s, _ = lam.laminate_matrices(q_t300, [12, -60, 45, 87], T_PLY)
    for M in (A_s, D_s):
        pp = pol.polar_parameters(M)
        assert pp["T0"] == pytest.approx(pp_ply["T0"], rel=1e-12)
        assert pp["T1"] == pytest.approx(pp_ply["T1"], rel=1e-12)
