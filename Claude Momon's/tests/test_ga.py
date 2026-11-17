"""Checks of the GA building blocks (encoding, rejection, operators)."""

import numpy as np

import ga


def test_codes_bits_round_trip():
    codes = np.array([[0, 1, 179], [128, 255, 42]])
    bits = ga.codes_to_bits(codes)
    assert bits.shape == (2, 24)
    assert np.array_equal(ga.bits_to_codes(bits, 3), codes)


def test_decoding_covers_the_angle_range():
    """Codes 0..179 give exactly the 180 angles -89..90, once each."""
    codes = np.arange(180).reshape(1, -1)
    angles = ga.decode_population(ga.codes_to_bits(codes), 180)[0]
    assert angles[0] == -89 and angles[-1] == 90
    assert len(np.unique(angles)) == 180


def test_initial_population_is_valid():
    rng = np.random.default_rng(0)
    pop = ga.init_population(200, 20, rng)
    assert ga.bits_to_codes(pop, 20).max() < ga.N_VALID_CODES


def test_rejection_restores_parent_gene():
    parents = ga.codes_to_bits(np.array([[10, 20]]))
    children = ga.codes_to_bits(np.array([[200, 21]]))   # first gene invalid
    repaired, n_rejected = ga.reject_invalid_genes(children, parents, 2)
    assert n_rejected == 1
    assert ga.bits_to_codes(repaired, 2).tolist() == [[10, 21]]


def test_operators_keep_population_valid():
    """After crossover + mutation + rejection, every code is valid."""
    rng = np.random.default_rng(1)
    parents = ga.init_population(100, 20, rng)
    children = ga.crossover_population(parents, 1.0, rng)
    children = ga.mutate_population(children, 0.5, 20, rng)
    children, _ = ga.reject_invalid_genes(children, parents, 20)
    assert ga.bits_to_codes(children, 20).max() < ga.N_VALID_CODES


def test_mutation_flips_one_bit_per_mutated_gene():
    rng = np.random.default_rng(2)
    pop = ga.init_population(50, 20, rng)
    mutated = ga.mutate_population(pop, 1.0, 20, rng)   # every gene mutates
    flips = (mutated != pop).reshape(50, 20, 8).sum(axis=2)
    assert np.all(flips == 1)
