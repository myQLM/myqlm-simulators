# -*- coding: utf-8 -*-
"""
@authors Bertrand Marchand
@brief pylinalg simulator service
@copyright 2017  Bull S.A.S.  -  All rights reserved.\n
           This is not Free or Open Source software.\n
           Please contact Bull SAS for details about its license.\n
           Bull - Rue Jean Jaurès - B.P. 68 - 78340 Les Clayes-sous-Bois
@namespace qat.pylinalg
"""

import numpy as np

import qat.comm.datamodel.ttypes as qat_datamodel
import qat.comm.task.ttypes as task_types
import qat.core.formula_eval as feval

def output_state_vector(circuit):
    """
    Computes state vector at the output of provided circuit.

    State vector is stored as numpy nd-array. 
    It is initialized at |0...0>.
    Then, loop over gates, updating the state vector using np.tensordot

    Args:
        circuit: input circuit

    Returns: 
        state_vec: nd-array containing final state vector.
    """

    # Initialization at |0...0>
    shape = tuple(2 for _ in range(circuit.nbqbits)) 
    state_vec = np.zeros(shape, dtype=np.complex128)
    state_vec[tuple(0 for _ in range(circuit.nbqbits))] = 1

    # cbits initilization.
    cbits = [0] * circuit.nbcbits

    # Loop over gates.
    for op_pos, op in enumerate(circuit.ops):

        if op.type == qat_datamodel.OpType.MEASURE:
            # measure op.qubits on state_vec and store in op.cbits
            measure(state_vec, op.qubits, op.cbits)
            continue

        if op.type == qat_datamodel.OpType.RESET:
            # measure, if result is 1 apply X.
            reset(state_vec, op.qubits)
            for cb in op.cbits:
                cbits[cb] = 0
            continue

        if op.type == qat_datamodel.OpType.CLASSIC:
            # compute result bit of formula
            cbits[op.cbits[0]] = int(feval.evaluate(op.formula, cbits))
            continue

        if op.type == qat_datamodel.OpType.BREAK:
            # evaluate formula and break if verdict is 1.
            verdict = feval.evaluate(op.formula, cbits)
            if verdict:
                raise_break(op, op_pos)      
            continue

        if op.type == qat_datamodel.OpType.CLASSICCTRL:
            # continue only if control cbits are all at 1.
            if not all([cbits[x] for x in op.cbits]):
                continue

        gdef = circuit.gateDic[op.gate]   # retrieving useful info.
        matrix = mat2nparray(gdef.matrix) # convert matrix to numpy array.

        #reshape for easy application.
        tensor = matrix.reshape(tuple(2 for _ in range(2*gdef.arity)))

        #axes for tensor dot: last indices of gate tensor.
        gate_axes = [k for k in range(gdef.arity, 2*gdef.arity, 1)]
        
        # actual gate application
        state_vec = np.tensordot(tensor, state_vec, axes=(gate_axes, op.qbits))

    return state_vec


def mat2nparray(matrix):
    """
    Converts serialized matrix format into numpy array.
    """

    A = np.empty((matrix.nRows, matrix.nCols), dtype=np.complex128) 
           
    cnt = 0
    for i in range(matrix.nRows):
        for j in range(matrix.nCols):
            A[i,j] = matrix.data[cnt].re + 1j*matrix.data[cnt].im
            cnt += 1

    return A   

def raise_break(op, op_pos):
     
    exp = task_types.RuntimeException(task_types.Error_Type.BREAK)
    exp.modulename = "PYLINALG"
    present_cbits = []
    for i in op.formula.split(" "):
        try:
            present_cbits += [int(i)]
        except ValueError:
            pass
    exp.message = "BREAK at gate #{} : formula : {}, cbits : {}"\
        .format(op_pos, op.formula,
                [(k, bool(cbits[k])) for k in present_cbits])
    raise exp
