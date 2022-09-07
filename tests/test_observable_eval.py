# -*- coding: utf-8 -*-

"""
    Licensed to the Apache Software Foundation (ASF) under one
    or more contributor license agreements.  See the NOTICE file
    distributed with this work for additional information
    regarding copyright ownership.  The ASF licenses this file
    to you under the Apache License, Version 2.0 (the
    "License"); you may not use this file except in compliance
    with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing,
    software distributed under the License is distributed on an
    "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
    KIND, either express or implied.  See the License for the
    specific language governing permissions and limitations
    under the License.
"""

"""
Tests for logic gates and classically controlled gates
"""

import numpy as np

from qat.lang.AQASM import Program, X, Z, PH, H

from qat.core import Observable, Term
from qat.comm.exceptions.ttypes import QPUException

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


class TestRaiseExceptNbshotsFinite(unittest.TestCase):
    def test_basic(self):
        with self.assertRaises(QPUException):
            prog = Program()
            qbits = prog.qalloc(1)
            prog.apply(X, qbits)
            circ = prog.to_circ()

            obs = Observable(1, pauli_terms=[Term(1., "Z", [0])])
            job = circ.to_job("OBS", observable=obs, nbshots=10)

            qpu = PyLinalg()

            result = qpu.submit(job)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
