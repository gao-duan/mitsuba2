from mitsuba.scalar_rgb.core import RadicalInverse
from mitsuba.scalar_rgb.core import PacketSize
from mitsuba.scalar_rgb.core.math import OneMinusEpsilon
import numpy as np


def r_inv(divisor, index):
    factor = 1
    value = 0
    recip = 1.0 / divisor

    while index != 0:
        next_val = index // divisor
        factor *= recip
        value = value * divisor + index - next_val * divisor
        index = next_val

    return value * factor


def gen_primes():
    # http://code.activestate.com/recipes/117119/
    D = {}
    q = 2
    while True:
        if q not in D:
            yield q
            D[q * q] = [q]
        else:
            for p in D[q]:
                D.setdefault(p + q, []).append(p)
            del D[q]
        q += 1


def test01_radical_inverse():
    v = RadicalInverse()
    assert(v.eval(0, 0) == 0)
    assert(v.eval(0, 1) == 0.5)
    assert(v.eval(0, 2) == 0.25)
    assert(v.eval(0, 3) == 0.75)

    for index, prime in enumerate(gen_primes()):
        if index >= 1024:
            break
        for i in range(10):
            assert np.abs(r_inv(prime, i) - v.eval(index, i)) < 1e-7


def test02_radical_inverse_vectorized():
    v = RadicalInverse()
    for index, prime in enumerate(gen_primes()):
        if index >= 1024:
            break
        result = v.eval(index, np.arange(10, dtype=np.uint64))
        for i in range(len(result)):
            assert np.abs(r_inv(prime, i) - result[i]) < 1e-7


def test03_faure_permutations():
    p = RadicalInverse()
    assert np.all(p.permutation(0) == [0, 1])
    assert np.all(p.permutation(1) == [0, 1, 2])
    assert np.all(p.permutation(2) == [0, 3, 2, 1, 4])
    assert np.all(p.permutation(3) == [0, 2, 5, 3, 1, 4, 6])


def test04_scrambled_radical_inverse():
    p = RadicalInverse(10, -1)
    assert np.all(p.permutation(0) == [0, 1])

    values = [
        0.0, 0.5, 0.25, 0.75, 0.125, 0.625, 0.375, 0.875, 0.0625, 0.5625,
        0.3125, 0.8125, 0.1875, 0.6875, 0.4375
    ]

    for i in range(len(values)):
        assert(p.eval_scrambled(0, i) == values[i])

    p = RadicalInverse(10, 3)
    assert np.all(p.permutation(0) == [1, 0])

    values_scrambled = [
        OneMinusEpsilon,
        0.5, 0.75, 0.25, 0.875, 0.375, 0.625, 0.125, 0.9375, 0.4375,
        0.6875, 0.1875, 0.8125, 0.3125, 0.5625
    ]

    for i in range(len(values_scrambled)):
        assert(p.eval_scrambled(0, i) == values_scrambled[i])


def test02_radical_inverse_vectorized():
    v = RadicalInverse()
    for index in range(1024):
        result = v.eval_scrambled(index, np.arange(10, dtype=np.uint64))
        for i in range(len(result)):
            assert np.abs(v.eval_scrambled(index, i) - result[i]) < 1e-7
