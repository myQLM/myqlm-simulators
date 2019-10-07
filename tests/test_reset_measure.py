"""
Unit tests
"""
import unittest
from qat.core.task import Task
from qat.lang.AQASM import Program, H
from qat.pylinalg import get_qpu_server as get_pylinalg_qpu
from qat.pylinalg import PyLinalg


class TestReset(unittest.TestCase):
    def test_reset(self):
        """test that reset gate works
        FIXME in 'analyze' mode, not testing intermediate_measurements
        FIXME not testing if resetting several qbits
        """
        # program with final state: qbit 0 : 0 with 100% prob,
        # but intermediate measure can be 0 or 1 with 50% prob
        prog = Program()
        reg = prog.qalloc(1)
        prog.apply(H, reg)
        prog.reset(reg)
        circ = prog.to_circ()

        ref_task = Task(circ, get_pylinalg_qpu())
        for res in ref_task.execute(nb_samples=5):

            self.assertEqual(res.state.int, 0)
            self.assertAlmostEqual(res.intermediate_measurements[0].probability, 0.5, delta=1e-10)

class TestMeasure(unittest.TestCase):
    def test_measure(self):
        """test that state indexing is same as other simulation services"""
        # program with final state: qbit 0 : 0 or 1 with 50% proba
        prog = Program()
        reg = prog.qalloc(1)
        creg = prog.calloc(1)
        prog.apply(H, reg)
        prog.measure(reg, creg)
        circ = prog.to_circ()

        qpu = PyLinalg()

        result = qpu.submit(circ.to_job(nbshots=5, aggregate_data=False))
        for res in result:

            self.assertAlmostEqual(res.intermediate_measurements[0].probability, 0.5, delta=1e-10)
            self.assertEqual(res.intermediate_measurements[0].cbits[0], res.state.int)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
