import os
import unittest

from qat.core.task import Task
from qat.core.circ import readcirc
from qat.pylinalg import get_qpu_server

BSM_TESTDIR = os.getenv("TESTS_DIR")

class TestSimpleCircExec(unittest.TestCase):

    def test_default_mode(self):
   
        fname = os.path.join(BSM_TESTDIR, "bellstate.circ") 
        circuit = readcirc(fname)

        task = Task(circuit, get_qpu_server())

        result = task.execute()

        self.assertTrue(result.state[0]==result.state[1])


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
