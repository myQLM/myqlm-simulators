import os
import unittest
import numpy as np

from qat.lang.AQASM import Program, CNOT, S, H, T, X
from qat.core.task import Task
from qat.core.wrappers import Circuit
from qat.pylinalg.service import PyLinalg
from qat.pylinalg import get_qpu_server

import qat.comm.exceptions.ttypes as exception_types

import glob

BSM_TESTDIR = os.getenv("TESTS_DIR")
CIRC_PATH = os.path.join(BSM_TESTDIR, "circuits")


class TestSimpleCircExec(unittest.TestCase):

    def test_default_mode(self):

        fname = os.path.join(CIRC_PATH, "bellstate.circ")

        circuit = Circuit().load(fname)

        task = Task(circuit, get_qpu_server())

        result = task.execute()

        self.assertTrue(result.state[0] == result.state[1])

    def test_analyze_mode(self):

        fname = os.path.join(CIRC_PATH, "bellstate.circ")
        circuit = Circuit().load(fname)

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


class TestControlFlow(unittest.TestCase):

    def test_break(self):

        circname = os.path.join(CIRC_PATH, "break.circ")

        circ = Circuit().load(circname)

        task = Task(circ, get_qpu_server())

        exp = exception_types.QPUException(exception_types.ErrorType.BREAK)

        raised = False

        try:
            res = task.execute()
        except exception_types.QPUException as Exp:
            self.assertEqual(Exp.code, 10)
            self.assertEqual(Exp.modulename, "PYLINALG")
            self.assertEqual(Exp.gate_index, 3)
            raised = True

        self.assertTrue(raised)

    def test_formula_and_cctrl(self):

        circname = os.path.join(CIRC_PATH, "boolean.circ")

        circ = Circuit().load(circname)

        task = Task(circ, get_qpu_server())

        res = task.execute()

        self.assertEqual(res.state.int, 7)


class TestBitOrder(unittest.TestCase):

    def test_state_indexing(self):
        """
        Args:
            qpu (QProc): a qpu
            expected_res (int): the expected result
            qbits (list<int>): list of qbits to measure
            n_shots (int): number of shots. If 0, return all nonzero amplitudes
        """

        fname = os.path.join(CIRC_PATH, "bit_ordering.circ")
        circ = Circuit().load(fname)

        for n_shots in [0, 10]:
            for expected_res, qbits in [(2, [0, 1, 2, 3]), (1, [0, 1, 2])]:

                ref_task = Task(circ, get_qpu_server())
                if n_shots == 0:
                    for res in ref_task.states(qbits=qbits):
                        self.assertEqual(res.state.int, expected_res)
                else:
                    for res in ref_task.execute(nb_samples=n_shots, qbits=qbits):
                        self.assertEqual(res.state.int, expected_res)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
