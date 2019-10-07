#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for logic gates and classically controlled gates
"""
import unittest
from qat.core.task import Task
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
        task = Task(circ, get_pylinalg_qpu())

        for res in task.states():
            self.assertEqual(res.intermediate_measurements[0].cbits[0], 1)
            self.assertEqual(res.intermediate_measurements[1].cbits[0], 1)

class TestLogicGates(unittest.TestCase):
    def test_logic(self):
        circ = make_simple_logic()
        task = Task(circ, get_pylinalg_qpu())

        for res in task.states():
            self.assertEqual(int(res.intermediate_measurements[0].cbits[0]), 1)
            self.assertEqual(int(res.intermediate_measurements[1].cbits[0]), 0)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
