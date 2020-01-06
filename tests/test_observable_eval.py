# -*- coding: utf-8 -*-
"""
Tests for logic gates and classically controlled gates
"""
import numpy as np

from qat.lang.AQASM import Program, X, Z, PH, H

from qat.core import Observable, Term

###################################
# Setting up QPU's test classes
###################################
import unittest
from qat.pylinalg import PyLinalg
from qat.lang.AQASM import Program, CNOT, S, H, T, X

class TestSimpleObservables(unittest.TestCase):

    def test_sample_1qb_Z(self):

        prog = Program()
        qbits = prog.qalloc(1)
        prog.apply(X, qbits)
        circ = prog.to_circ()

        obs = Observable(1, pauli_terms=[Term(1., "Z", [0])])
        job = circ.to_job("OBS", observable=obs)

        qpu = PyLinalg()

        result = qpu.submit(job)
        self.assertAlmostEqual(result.value, -1)

        obs = Observable(1, pauli_terms=[Term(18., "Z", [0])])
        job = circ.to_job("OBS", observable=obs)

        result = qpu.submit(job)
        self.assertAlmostEqual(result.value, -18)

        prog = Program()
        qbits = prog.qalloc(1)
        circ = prog.to_circ()

        obs = Observable(1, pauli_terms=[Term(1., "Z", [0])])
        job = circ.to_job("OBS", observable=obs)

        result = qpu.submit(job)
        self.assertAlmostEqual(result.value, 1)

        obs = Observable(1, pauli_terms=[Term(18., "Z", [0])])
        job = circ.to_job("OBS", observable=obs)

        result = qpu.submit(job)
        self.assertAlmostEqual(result.value, 18)


    def test_sample_1qb_X(self):

        prog = Program()
        qbits = prog.qalloc(1)
        prog.apply(H, qbits)
        prog.apply(Z, qbits)
        circ = prog.to_circ()

        obs = Observable(1, pauli_terms=[Term(1., "X", [0])])
        job = circ.to_job("OBS", observable=obs)

        qpu = PyLinalg()
        result = qpu.submit(job)
        self.assertAlmostEqual(result.value, -1)

        obs = Observable(1, pauli_terms=[Term(18., "X", [0])])
        job = circ.to_job("OBS", observable=obs)

        result = qpu.submit(job)
        self.assertAlmostEqual(result.value, -18)

        prog = Program()
        qbits = prog.qalloc(1)
        prog.apply(H, qbits)
        circ = prog.to_circ()

        obs = Observable(1, pauli_terms=[Term(1., "X", [0])])
        job = circ.to_job("OBS", observable=obs)

        result = qpu.submit(job)
        self.assertAlmostEqual(result.value, 1)

        obs = Observable(1, pauli_terms=[Term(18., "X", [0])])
        job = circ.to_job("OBS", observable=obs)

        result = qpu.submit(job)
        self.assertAlmostEqual(result.value, 18)


    def test_sample_1qb_Y(self):

        prog = Program()
        qbits = prog.qalloc(1)
        prog.apply(H, qbits)
        prog.apply(PH(-np.pi/2), qbits)
        circ = prog.to_circ()

        obs = Observable(1, pauli_terms=[Term(1., "Y", [0])])
        job = circ.to_job("OBS", observable=obs)

        qpu = PyLinalg()
        result = qpu.submit(job)
        self.assertAlmostEqual(result.value, -1)

        obs = Observable(1, pauli_terms=[Term(18., "Y", [0])])
        job = circ.to_job("OBS", observable=obs)

        result = qpu.submit(job)
        self.assertAlmostEqual(result.value, -18)

        prog = Program()
        qbits = prog.qalloc(1)
        prog.apply(H, qbits)
        prog.apply(PH(np.pi/2), qbits)
        circ = prog.to_circ()

        obs = Observable(1, pauli_terms=[Term(1., "Y", [0])])
        job = circ.to_job("OBS", observable=obs)

        result = qpu.submit(job)
        self.assertAlmostEqual(result.value, 1)

        obs = Observable(1, pauli_terms=[Term(18., "Y", [0])])
        job = circ.to_job("OBS", observable=obs)

        result = qpu.submit(job)
        self.assertAlmostEqual(result.value, 18)

    def test_sample_2qb_several_terms(self):

        qpu = PyLinalg()
        prog = Program()
        qbits = prog.qalloc(2)
        prog.apply(X, qbits[0])
        circ = prog.to_circ()

        obs = Observable(2, pauli_terms=[
            Term(1., "ZZ", [0, 1]),
            Term(2., "XX", [0, 1]),
        ])
        job = circ.to_job("OBS", observable=obs)

        result = qpu.submit(job)
        self.assertAlmostEqual(result.value, -1)

        prog = Program()
        qbits = prog.qalloc(2)
        prog.apply(X, qbits[0])
        prog.apply(X, qbits[1])
        circ = prog.to_circ()

        obs = Observable(2, pauli_terms=[
            Term(1., "ZZ", [0, 1]),
            Term(2., "XX", [0, 1]),
        ])
        job = circ.to_job("OBS", observable=obs)

        result = qpu.submit(job)
        self.assertAlmostEqual(result.value, 1)

        prog = Program()
        qbits = prog.qalloc(2)
        prog.apply(H, qbits[0])
        prog.apply(H, qbits[1])
        prog.apply(Z, qbits[1])
        circ = prog.to_circ()

        obs = Observable(2, pauli_terms=[
            Term(1., "ZZ", [0, 1]),
            Term(2., "XX", [0, 1]),
        ])
        job = circ.to_job("OBS", observable=obs)

        result = qpu.submit(job)
        self.assertAlmostEqual(result.value, -2)


    def test_sample_2qb(self):

        qpu = PyLinalg()
        prog = Program()
        qbits = prog.qalloc(2)
        prog.apply(X, qbits[0])
        circ = prog.to_circ()

        obs = Observable(2, pauli_terms=[Term(1., "ZZ", [0, 1])])
        job = circ.to_job("OBS", observable=obs)

        result = qpu.submit(job)
        self.assertAlmostEqual(result.value, -1)

        prog = Program()
        qbits = prog.qalloc(2)
        prog.apply(X, qbits[0])

        prog.apply(X, qbits[1])
        circ = prog.to_circ()

        obs = Observable(2, pauli_terms=[Term(1., "ZZ", [0, 1])])
        job = circ.to_job("OBS", observable=obs)

        result = qpu.submit(job)
        self.assertAlmostEqual(result.value, 1)


    def test_bitorder_obs(self):

        qpu = PyLinalg()
        prog = Program()
        qbits = prog.qalloc(2)
        prog.apply(X, qbits[0])
        circ = prog.to_circ()
        obs = Observable(2, pauli_terms=[Term(1., "Z", [0])])
        job = circ.to_job("OBS", observable=obs)
        result = qpu.submit(job)
        self.assertAlmostEqual(result.value, -1)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
