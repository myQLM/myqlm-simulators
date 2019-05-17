import os
import unittest

from qat.core.task import Task
from qat.core import Circuit
from qat.pylinalg import get_qpu_server
from qat.linalg import get_qpu_server as get_linalg_qpu_server

import glob

BSM_TESTDIR = os.getenv("TESTS_DIR")
CIRC_PATH = os.path.join(BSM_TESTDIR, "circuits")

class TestSimpleCircExec(unittest.TestCase):

    def test_default_mode(self):
        """ Testing default mode """
        fname = os.path.join(CIRC_PATH, "bellstate.circ")
        circuit = Circuit.load(fname)

        task = Task(circuit, get_qpu_server())

        result = task.execute()

        self.assertEqual(result.state[0], result.state[1])

    def test_analyze_mode(self):

        fname = os.path.join(CIRC_PATH, "bellstate.circ")
        circuit = Circuit.load(fname)

        task = Task(circuit, get_qpu_server())

        for state in task.states():
            pass

class TestLinalgCompare(unittest.TestCase):

    def test_linalg_compare(self):

        condition = os.path.join(CIRC_PATH, "*.circ")
        fnames = glob.glob(condition)

        circuits = []

        for name in fnames:
            circ = Circuit.load(name)
            no = False
            if len(circ.ops) > 1000:
                no = True
            if circ.nbqbits > 10:
                no = True
            for op in circ.ops:
                if op.type not in [0,2]:
                    no = True
            if no: #oh no
                break
            circuits.append(circ)

        for circ in circuits:
            task1 = Task(circ, get_qpu_server())
            task2 = Task(circ, get_linalg_qpu_server())

            res1 = {}
            res2 = {}

            for state in task1.states():
                print(state)
                res1[state.state.int] = state.amplitude

            for state in task2.states():
                res2[state.state.int] = state.amplitude

            for st in res1.keys():
                print(res1[st], res2[st])
                self.assertAlmostEqual(res1[st], res2[st])

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
