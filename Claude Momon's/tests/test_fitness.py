"""Vérifications de la fonction de coût et de la fitness."""

import numpy as np
import pytest

import fitness as fit
import laminate as lam
import polar as pol

T_PLY = 0.125


@pytest.fixture
def q_t300():
    """Rigidité réduite du pli T300/5208 (P2 slide 49)."""
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
    """Un seul pli : A* = D* = Q, donc Phi4 = Phi8 = 1, Phi2 = 0, Phi3 = 0."""
    pp_ply = pol.polar_parameters(q_t300)
    phi = fit.partial_objectives(*fit.laminate_polar(q_t300, [0], T_PLY), pp_ply)
    assert phi[2] == pytest.approx(0.0, abs=1e-20)
    assert phi[4] == pytest.approx(1.0)
    assert phi[8] == pytest.approx(1.0)
    assert phi[3] == pytest.approx(0.0, abs=1e-20)


def test_slide_51_cost(q_t300):
    """P2 slides 49-51 : [9/0/18/-4/14/5] avec Phi1 + Phi3 + Phi7 + Phi11.

    Décision du groupe : on garde la formule de la slide 45,
    Phi1 = (||B*|| / ||Q||)^2 avec B* = 2B/h^2 (la définition de l'énoncé et
    du tableau polaire de la slide 51). Avec elle, le coût vaut 9,9648e-8.

    La slide affiche 3,5873e-6, exactement n^2 = 36 fois plus : cela
    correspond à Phi1 calculé avec n * B* au lieu de B*. On considère que
    c'est une erreur d'application numérique sur la slide. Ce test
    documente les deux faits.
    """
    n = 6
    value = fit.cost([9, 0, 18, -4, 14, 5], q_t300, T_PLY, [1, 3, 7, 11])
    # Notre valeur, avec la formule de la slide 45
    assert value == pytest.approx(9.9648e-8, rel=1e-4)
    # On retrouve la valeur de la slide avec le facteur n^2 en plus
    assert value * n**2 == pytest.approx(3.5873e-6, rel=1e-4)


def test_incompatible_objectives_rejected():
    with pytest.raises(ValueError):
        fit.check_objectives([1, 3, 4])
    with pytest.raises(ValueError):
        fit.check_objectives([7, 9])
    with pytest.raises(ValueError):
        fit.check_objectives([1, 12])       # objectif inconnu
    fit.check_objectives([1, 4, 9])         # groupe 1 : autorisé
    fit.check_objectives([1, 4, 8])         # autre lecture possible : autorisée
