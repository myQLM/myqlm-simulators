import os
import unittest
import numpy as np
import glob

import qat.comm.exceptions.ttypes as exception_types
from qat.core.task import Task
from qat.core.wrappers import Circuit
from qat.lang.AQASM import Program, CNOT, S, H, T, X
from qat.pylinalg import PyLinalg
from qat.pylinalg import get_qpu_server



def generate_bell_state():
    prog = Program()
    qbits = prog.qalloc(2)
    prog.apply(H, qbits[0])
    prog.apply(CNOT, qbits)
    return prog.to_circ()

def generate_break():
    prog = Program()
    qbits = prog.qalloc(3)
    cbits = prog.calloc(3)
    prog.apply(X, qbits[1])
    prog.measure(qbits[0], cbits[0])
    prog.measure(qbits[1], cbits[1])
    prog.cbreak(cbits[1] & (~ cbits[0]))
    return prog.to_circ()

def generate_boolean():
    prog = Program()
    qbits = prog.qalloc(3)
    cbits = prog.calloc(3)
    prog.apply(X, qbits[1])
    prog.measure(qbits[0], cbits[0])
    prog.measure(qbits[1], cbits[1])
    prog.logic(cbits[2], cbits[1] & ~ cbits[0])
    prog.cc_apply(cbits[2], X, qbits[2])
    prog.apply(X, qbits[0])
    return prog.to_circ()

def generate_bit_ordering():
    prog = Program()
    qbits = prog.qalloc(4)
    prog.apply(X, qbits[2])
    return prog.to_circ()



class TestSimpleCircExec(unittest.TestCase):

    def test_default_mode(self):

        circuit = generate_bell_state()
        task = Task(circuit, get_qpu_server())
        result = task.execute()
        self.assertTrue(result.state.int == result.state.int)

    def test_analyze_mode(self):

        circuit = generate_bell_state()
        task = Task(circuit, get_qpu_server())

        for state in task.states():
            self.assertAlmostEqual(state.probability, 0.5)

    def test_normal_launch_mode(self):

        # Create a small program
        prog = Program()
        qubits = prog.qalloc(2)
        prog.apply(H, qubits[0])
        prog.apply(CNOT, qubits)

        circ = prog.to_circ()

        # Simulate
        job = circ.to_job()
        qpu = PyLinalg()
        result = qpu.submit_job(job)

        self.assertEqual(len(result.raw_data),2)

        self.assertAlmostEqual(result.raw_data[0].probability, 0.5)
        self.assertTrue(result.raw_data[0].state.int in [0,3])
        self.assertTrue(result.raw_data[1].state.int in [0,3])

    def test_normal_launch_mode_subset_qb(self):

        # Create a small program
        prog = Program()
        qubits = prog.qalloc(2)
        prog.apply(H, qubits[0])
        prog.apply(CNOT, qubits)

        circ = prog.to_circ()

        # Simulate
        job = circ.to_job(qubits=[0])
        qpu = PyLinalg()
        result = qpu.submit_job(job)

        self.assertEqual(len(result.raw_data),2)

        self.assertAlmostEqual(result.raw_data[0].probability, 0.5)
        self.assertTrue(result.raw_data[0].state.int in [0,1])
        self.assertTrue(result.raw_data[1].state.int in [0,1])

    def test_normal_launch_mode_with_nbshots(self):

        # Create a small program
        prog = Program()
        qubits = prog.qalloc(2)
        prog.apply(H, qubits[0])
        prog.apply(CNOT, qubits)

        circ = prog.to_circ()

        # Simulate
        job = circ.to_job(nbshots=4, aggregate_data=False)
        qpu = PyLinalg()
        result = qpu.submit_job(job)

        self.assertEqual(len(result.raw_data),4)
        self.assertEqual(result.raw_data[0].probability, None) #no prob if not aggregating data

    def test_normal_launch_mode_with_nbshots_and_qbs(self):

        # Create a small program
        prog = Program()
        qubits = prog.qalloc(2)
        prog.apply(H, qubits[0])
        prog.apply(CNOT, qubits)

        circ = prog.to_circ()

        # Simulate
        job = circ.to_job(nbshots=4, qubits=[0], aggregate_data=False)
        qpu = PyLinalg()
        result = qpu.submit_job(job)

        self.assertEqual(len(result.raw_data),4)

        self.assertEqual(result.raw_data[0].probability, None) #No probability if not aggregating data
        for rd in result.raw_data:
            self.assertTrue(rd.state.int in [0,1],
                            msg="state= %s"%rd.state)

class TestControlFlow(unittest.TestCase):

    def test_break(self):

        circ = generate_break()
        task = Task(circ, get_qpu_server())
        exp = exception_types.QPUException(exception_types.ErrorType.BREAK)
        exp = exception_types.QPUException(exception_types.ErrorType.BREAK)
        raised = False

        try:
            res = task.execute()
        except exception_types.QPUException as Exp:
            self.assertEqual(Exp.code, 10)
            self.assertEqual(Exp.modulename, "qat.pylinalg")
            raised = True

        self.assertTrue(raised)

    def test_formula_and_cctrl(self):

        circ = generate_boolean()
        task = Task(circ, get_qpu_server())
        res = task.execute()
        self.assertEqual(res.state.int, 7)


class TestBitOrder(unittest.TestCase):

    def test_bit_ordering(self):
        circ = generate_bit_ordering()
        for n_shots in [0, 10]:
#            for expected_res, qbits in [(2, [0, 1, 2, 3]), (1, [0, 1, 2])]:
            for expected_res, qbits in [(2, [0, 1, 2, 3]),
                                        (1, [0, 1, 2]),
                                        (2, [2, 3]),
                                        (1, [3, 2])]:

                ref_task = Task(circ, get_qpu_server())
                if n_shots == 0:
                    for res in ref_task.states(qbits=qbits):
                        self.assertEqual(res.state.int, expected_res)
                else:
                    for res in ref_task.execute(nb_samples=n_shots, qbits=qbits):
                        self.assertEqual(res.state.int, expected_res)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
