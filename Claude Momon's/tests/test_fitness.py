"""Checks of the cost function and of the fitness."""

import numpy as np
import pytest

import fitness as fit
import laminate as lam
import polar as pol

T_PLY = 0.125


@pytest.fixture
def q_t300():
    return lam.ply_stiffness(lam.ply_compliance(181000.0, 10300.0, 0.28, 7170.0))


def test_fitness_best_is_one_worst_is_zero():
    f = fit.fitness([3.0, 1.0, 2.0])
    assert f.tolist() == pytest.approx([0.0, 1.0, 0.5])


def test_fitness_constant_population():
    assert fit.fitness([2.0, 2.0]).tolist() == [1.0, 1.0]


def test_wrap_angle():
    assert fit.wrap_angle(np.pi / 2.0 - 0.01, np.pi / 2.0) == pytest.approx(-0.01)
    assert fit.wrap_angle(0.2, np.pi / 2.0) == pytest.approx(0.2)


def test_single_ply_objectives(q_t300):
    """A single ply: A* = D* = Q, so Phi4 = Phi8 = 1, Phi2 = 0, Phi3 = 0."""
    pp_ply = pol.polar_parameters(q_t300)
    phi = fit.partial_objectives(*fit.laminate_polar(q_t300, [0], T_PLY), pp_ply)
    assert phi[2] == pytest.approx(0.0, abs=1e-20)
    assert phi[4] == pytest.approx(1.0)
    assert phi[8] == pytest.approx(1.0)
    assert phi[3] == pytest.approx(0.0, abs=1e-20)


def test_slide_51_cost(q_t300):
    """P2 slides 49-51: [9/0/18/-4/14/5] with Phi1 + Phi3 + Phi7 + Phi11.

    Group decision: we keep the formula of slide 45, Phi1 = (||B*|| / ||Q||)^2
    with B* = 2B/h^2 (the definition used by the statement and by the polar
    table of slide 51). With it the cost is 9.9648e-8.

    The slide prints 3.5873e-6, which is exactly n^2 = 36 times larger: it
    corresponds to Phi1 computed with n * B* instead of B*. We treat it as a
    numerical slip on the slide. This test documents both facts.
    """
    n = 6
    value = fit.cost([9, 0, 18, -4, 14, 5], q_t300, T_PLY, [1, 3, 7, 11])
    # Our value, with the slide 45 formula
    assert value == pytest.approx(9.9648e-8, rel=1e-4)
    # The slide value is recovered with the extra factor n^2
    assert value * n**2 == pytest.approx(3.5873e-6, rel=1e-4)


def test_incompatible_objectives_rejected():
    with pytest.raises(ValueError):
        fit.check_objectives([1, 3, 4])
    with pytest.raises(ValueError):
        fit.check_objectives([7, 9])
    fit.check_objectives([1, 4, 9])     # group 1: allowed
