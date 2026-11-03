# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 22:06:49 2024

@author: nicol
"""

import numpy as np

def rastrigin(x):
    """ fonction Rastrigin """
    A = 10
    return A * len(x) + sum([(xi ** 2 - A * np.cos(2 * np.pi * xi)) for xi in x])


def ackley(x):
    """fonction Ackley"""
    a = 20
    b = 0.2
    c = 2 * np.pi
    d = len(x)
    sum1 = sum([xi ** 2 for xi in x])
    sum2 = sum([np.cos(c * xi) for xi in x])
    return -a * np.exp(-b * np.sqrt(sum1 / d)) - np.exp(sum2 / d) + a + np.exp(1)


def sphere(x):
    """Fonction Sphere"""
    return sum([xi ** 2 for xi in x])


def holder_table(x):
    """Hölder table function."""
    if len(x) != 2:
        raise ValueError("La fonction Hölder table function prend uniquement deux variables")
    x1, x2 = x
    return -abs(
        np.sin(x1) * np.cos(x2) * np.exp(abs(1 - (np.sqrt(x1 ** 2 + x2 ** 2) / np.pi)))
    )
