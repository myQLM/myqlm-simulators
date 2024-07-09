#!/usr/bin/env python
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

Tests for logic gates and classically controlled gates
"""

import unittest
from qat.lang.AQASM import Program, X
from qat.pylinalg import get_qpu_server as get_pylinalg_qpu


def make_simple_logic():
    prog = Program()
    qbits = prog.qalloc(2)
    cbits = prog.calloc(5)
    prog.apply(X, qbits[0])
    prog.measure(qbits[0], cbits[0])
    prog.measure(qbits[1], cbits[1])
    prog.logic(cbits[2], cbits[1] | cbits[0])
    prog.logic(cbits[3], cbits[2] & cbits[1])
    prog.logic(cbits[4], cbits[0] ^ cbits[1])
    return prog.to_circ()


def make_c_control_circuit():
    prog = Program()
    qbits = prog.qalloc(2)
    cbits = prog.calloc(2)
    prog.apply(X, qbits[0])
    prog.measure(qbits[0], cbits[0])
    prog.cc_apply(cbits[0], X, qbits[1])
    prog.measure(qbits[1], cbits[1])
    return prog.to_circ()


class TestClassicalControl(unittest.TestCase):
    def test_cc(self):
        circ = make_c_control_circuit()
        res = get_pylinalg_qpu().submit(circ.to_job(nbshots=10))

        for sample in res:
            self.assertEqual(sample.intermediate_measurements[0].cbits[0], 1)
            self.assertEqual(sample.intermediate_measurements[1].cbits[0], 1)


class TestLogicGates(unittest.TestCase):
    def test_logic(self):
        circ = make_simple_logic()
        res = get_pylinalg_qpu().submit(circ.to_job(nbshots=10))

        for sample in res:
            self.assertEqual(int(sample.intermediate_measurements[0].cbits[0]), 1)
            self.assertEqual(int(sample.intermediate_measurements[1].cbits[0]), 0)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
