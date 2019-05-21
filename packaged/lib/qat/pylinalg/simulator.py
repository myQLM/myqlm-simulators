# -*- coding: utf-8 -*-
"""
@authors Bertrand Marchand
@brief pylinalg simulator engine
@copyright 2019  Bull S.A.S.  -  All rights reserved.\n
           This is not Free or Open Source software.\n
           Please contact Bull SAS for details about its license.\n
           Bull - Rue Jean Jaurès - B.P. 68 - 78340 Les Clayes-sous-Bois
@namespace qat.pylinalg
"""

import numpy as np

import qat.comm.datamodel.ttypes as qat_datamodel
import qat.comm.exceptions.ttypes as exceptions_types
import qat.core.formula_eval as feval


def simulate(circuit):
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

    # history #TODO
    history = []

    # Loop over gates.
    for op_pos, op in enumerate(circuit.ops):

        if op.type == qat_datamodel.OpType.MEASURE:
            # measure op.qbits on state_vec and store in op.cbits
            intprob_list = measure(state_vec, op.qbits)
            state_vec = project(state_vec, op.qbits, intprob_list[0])
            res_int, p = intprob_list[0]
            for k, qb in enumerate(op.qbits):
                cbits[op.cbits[k]] = res_int >> k & 1
            continue

        if op.type == qat_datamodel.OpType.RESET:
            # measure, if result is 1 apply X.
            state_vec = reset(state_vec, op.qbits)
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
                raise_break(op, op_pos, cbits)      
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

        # moving axes back to correct positions
        cur_positions = range(len(op.qbits))
        state_vec = np.moveaxis(state_vec, cur_positions, op.qbits)

    return state_vec, history

def measure(state_vec, qubits, nb_samples=1):

    probs = np.abs(state_vec**2)

    all_qubits = [k for k in range(len(state_vec.shape))]
    sum_axes = tuple(qb for qb in all_qubits if qb not in qubits)

    probs = probs.sum(axis=sum_axes)

    cumul = np.cumsum(probs)

    intprob_list = []

    for _ in range(nb_samples):
 
        res_int = len(np.where(cumul < np.random.random())[0])

        str_bin_repr = np.binary_repr(res_int, width = len(qubits))
        index = tuple(int(s) for s in str_bin_repr)

        intprob_list.append((res_int, probs[index]))

    return intprob_list

def project(state_vec, qubits, intprob):

    all_qubits = [k for k in range(len(state_vec.shape))]

    state_int, prob = intprob

    index_assignment = []
    
    for qb in all_qubits:
        if qb in qubits:
            val = ( state_int >> qubits.index(qb) ) & 1 
            index_assignment.append(1 - val)
        else: 
            index_assignment.append(slice(None))

    state_vec[tuple(index_assignment)] = 0.
    state_vec /= np.sqrt(prob)
    
    return state_vec 

def reset(state_vec, qubits):
 
    X = np.array([[0,1],[1,0]], dtype=np.complex128)

    intprob_list = measure(state_vec, qubits)
    state_vec = project(state_vec, qubits, intprob_list[0])
    res_int, _ = intprob_list[0]
    str_bin_repr = np.binary_repr(res_int, width = len(qubits))

    for k, res in enumerate(str_bin_repr):
        if int(res) == 1:
            state_vec = np.tensordot(X, state_vec, axes=([1],[qubits[k]]))
            state_vec = np.moveaxis(state_vec, 0, qubits[k])

    return state_vec


def raise_break(op, op_pos, cbits):

    exp = exceptions_types.RuntimeException(exceptions_types.ErrorType.BREAK)
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
