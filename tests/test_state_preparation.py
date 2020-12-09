import unittest
import numpy as np
from qat.comm.exceptions.ttypes import QPUException
from qat.lang.AQASM import Program
from qat.lang.AQASM import AbstractGate, X
from qat.pylinalg import PyLinalg

class TestBasic(unittest.TestCase):
    def check_basic(self, vec):

        SP = AbstractGate("STATE_PREPARATION", [np.ndarray])

        prog = Program()
        reg = prog.qalloc(4)
        prog.apply(SP(vec), reg)
        qpu = PyLinalg()

        res = qpu.submit(prog.to_circ().to_job())

        statevec = np.zeros(2**4, np.complex)
        for sample in res:
            statevec[sample.state.int] = sample.amplitude
            
        assert(np.linalg.norm(vec - statevec) < 1e-16)

    def test_simple(self):
        vec = np.zeros(2**4, np.complex)
        vec[2] = 1.0 - 0.5j
        vec /= np.linalg.norm(vec)

        self.check_basic(vec)

    def test_raise_wrong_size(self):
        vec = np.zeros(2**3, np.complex)
        vec[2] = 1.0 - 0.5j
        vec /= np.linalg.norm(vec)

        with self.assertRaises(QPUException):
            self.check_basic(vec)

    def test_raise_wrong_norm(self):
        vec = np.zeros(2**4, np.complex)
        vec[2] = 1.0 - 0.5j

        with self.assertRaises(QPUException):
            self.check_basic(vec)
            
