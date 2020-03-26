from qat.lang.AQASM import Program, CNOT, S, H, T, X
from qat.pylinalg import PyLinalg
import numpy as np

def test_sv():

    prog = Program()
    qs = prog.qalloc(2)

    prog.apply(H, qs[0])
    prog.apply(CNOT, qs)

    circ = prog.to_circ()

    job1 = circ.to_job(nbshots=0, qubits=[0])
    job2 = circ.to_job(nbshots=10)

    qpu = PyLinalg()

    res1 = qpu.submit(job1)
    res2 = qpu.submit(job2)

    for s in res1:
        print(s)
        assert(np.allclose(s.probability,0.5))

    print("------")
    
    for t in res2:
        print(t)

