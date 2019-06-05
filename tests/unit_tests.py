import os
import unittest
import numpy as np

from qat.lang.AQASM import Program, CNOT, S, H, T, X
from qat.core.task import Task
from qat.core.wrappers import Circuit
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

        for _ in range(20):

            circ = random_circ(5, 50)
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

def random_circ(n, length):

    prog = Program()
    reg = prog.qalloc(n)

    l = ["H","S","T","CNOT"]

    for g in range(length):
        ident = np.random.choice(l)
        
        if ident=="CNOT":
            args = list(np.random.choice(np.arange(n),2,replace=False))
            prog.apply(CNOT, [reg[a] for a in args])
        elif ident=="H":
            arg = np.random.choice(np.arange(n))
            prog.apply(H, reg[arg])
        elif ident=="S":
            arg = np.random.choice(np.arange(n))
            prog.apply(S, reg[arg])
        elif ident=="T":
            arg = np.random.choice(np.arange(n))
            prog.apply(T, reg[arg])

    return prog.to_circ()

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
        circ = readcirc(fname)
#        prog = Program()
#        reg = prog.qalloc(4)
#        prog.apply(X, reg[2])
#        circ = prog.to_circ()

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
