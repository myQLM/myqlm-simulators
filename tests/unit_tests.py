import os
import unittest

from qat.core.task import Task
from qat.core.circ import readcirc
from qat.pylinalg import get_qpu_server
from qat.linalg import get_qpu_server as get_linalg_qpu_server

import qat.comm.task.ttypes as task_types

import glob

BSM_TESTDIR = os.getenv("TESTS_DIR")
CIRC_PATH = os.path.join(BSM_TESTDIR, "circuits")

class TestSimpleCircExec(unittest.TestCase):

    def test_default_mode(self):
   
        fname = os.path.join(CIRC_PATH, "bellstate.circ") 
        circuit = readcirc(fname)

        task = Task(circuit, get_qpu_server())

        result = task.execute()

        self.assertTrue(result.state[0]==result.state[1])

    def test_analyze_mode(self):

        fname = os.path.join(CIRC_PATH, "bellstate.circ") 
        circuit = readcirc(fname)

        task = Task(circuit, get_qpu_server())
       
        for state in task.states():
            pass 

class TestLinalgCompare(unittest.TestCase):

    def test_linalg_compare(self):

        condition = os.path.join(CIRC_PATH, "*.circ")
        fnames = glob.glob(condition)

        circuits = []

        for name in fnames:
            circ = readcirc(name)
            no = False
            if len(circ.ops) > 1000:
                no = True
            if circ.nbqbits > 10:
                no = True
            for op in circ.ops:
                if op.type > 0:
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
                res1[state.state.int] = state.amplitude
    
            for state in task2.states():
                res2[state.state.int] = state.amplitude

            for st in res1.keys():
                print(res1[st], res2[st])
                self.assertAlmostEqual(res1[st], res2[st])

class TestControlFlow(unittest.TestCase):

    def test_break(self):
        
        circname = os.path.join(CIRC_PATH, "break.circ")

        circ = readcirc(circname)
        
        task = Task(circ, get_qpu_server() )

        #exp = task_types.RuntimeException(task_types.Error_Type.BREAK)
        # TODO: check that the exception we want is raised, not just any.

        raised = False

        try:
            res = task.execute()
        except:
            raised = True

        self.assertTrue(raised)

    def test_formula_and_cctrl(self):

        circname = os.path.join(CIRC_PATH, "boolean.circ")

        circ = readcirc(circname)
        
        task = Task(circ, get_qpu_server())
         
        res = task.execute()
    
        self.assertEqual(res.state.int, 7) 

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
