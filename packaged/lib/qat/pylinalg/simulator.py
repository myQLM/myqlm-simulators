# -*- coding: utf-8 -*-
"""
| @authors Bertrand Marchand
| @brief pylinalg simulator engine
| @copyright 2019  Bull S.A.S.  -  All rights reserved.
|            This is not Free or Open Source software.
|            Please contact Bull SAS for details about its license.
|            Bull - Rue Jean Jaurès - B.P. 68 - 78340 Les Clayes-sous-Bois
| @namespace qat.pylinalg
"""

import numpy as np

import qat.comm.shared.ttypes as shared_types
import qat.comm.datamodel.ttypes as qat_datamodel
import qat.comm.exceptions.ttypes as exceptions_types
import qat.core.formula_eval as feval


def simulate(circuit):
    """
    Computes state vector at the output of provided circuit.

    State vector is stored as a :class:`numpy.ndarray`.
    It is initialized at |0...0>.
    Then, loop over gates, updating the state vector using `np.tensordot`

    Parameters
    ----------
    circuit : :class:`qat.comm.datamodel.ttypes.Circuit`
        Input circuit. The circuit to simulate.

    Returns
    -------
    :obj:`tuple`
        This function returns a tuple: state_vec, history.        
            - | state_vec: :class:`numpy.ndarray` containing the final 
              | state vector. It has one 2-valued index per qubits.
            - | history: :obj:`list` of :class:`qat.comm.shared_types.IntermediateMeasure`. 
              | List containing descriptors of the intermediate measurements 
              | that occured within the circuit, so that the classical branching is 
              | known to the user.

    """

    # Initialization at |0...0>
    shape = tuple([2 for _ in range(circuit.nbqbits)])
    state_vec = np.zeros(shape, dtype=np.complex128)
    state_vec[tuple([0 for _ in range(circuit.nbqbits)])] = 1

    # cbits initilization.
    cbits = [0] * circuit.nbcbits

    history = []

    # Loop over gates.
    for op_pos, op in enumerate(circuit.ops):

        if op.type == qat_datamodel.OpType.MEASURE:
            # measure op.qbits on state_vec and store in op.cbits
            intprob_list = measure(state_vec, op.qbits)
            state_vec = project(state_vec, op.qbits, intprob_list[0])
            res_int, p = intprob_list[0]

            for k, _ in enumerate(op.qbits):
                cbits[op.cbits[k]] = res_int >> k & 1
  
            history.append(shared_types.IntermediateMeasure(
                gate_pos=op_pos,
                cbits=[(res_int >> k & 1) for k in range(len(op.qbits))],
                probability=p
            ))
            continue

        if op.type == qat_datamodel.OpType.RESET:
            # measure, if result is 1 apply X.
            state_vec, res, prob = reset(state_vec, op.qbits)  # contains actual implem.
            for cb in op.cbits:
                cbits[cb] = 0
            history.append(shared_types.IntermediateMeasure(
                gate_pos=op_pos,
                cbits=res,
                probability=prob
            ))
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

        gdef = circuit.gateDic[op.gate]    # retrieving useful info.
        matrix = mat2nparray(gdef.matrix)  # convert matrix to numpy array.

        # reshape for easy application.
        tensor = matrix.reshape(tuple([2 for _ in range(2*gdef.arity)]))

        # axes for tensor dot: last indices of gate tensor.
        gate_axes = [k for k in range(gdef.arity, 2*gdef.arity, 1)]

        # actual gate application
        state_vec = np.tensordot(tensor, state_vec, axes=(gate_axes, op.qbits))

        # moving axes back to correct positions
        state_vec = np.moveaxis(state_vec, range(len(op.qbits)), op.qbits)

    return state_vec, history


def measure(state_vec, qubits, nb_samples=1):
    """
    Samples measurement results on the specified qubits.

    No projection is carried out ! See "project" function.
    Thanks to the absence of projection, several samples can be asked.


    Parameters
    ----------
    state_vec : :class:`numpy.ndarray` 
        The :class:`numpy.ndarray` containing full state vector.
    qubits : :obj:`list` 
        list of integers specifying the subset of qubits to measure.
    nb_samples : :obj:`int`
        the number of samples to return. Set to one by default.

    Returns
    -------
    :obj:`list`
        **intprob_list**: a list (of length nb_samples) containing tuples
        of the form (integer, probability). The integer is the result of
        the measurement on the subset of qubits (when converted to binary
        representation, it needs to have a width of len(qubits)).
        The probability is the probability the measurement had to occur.
        It is useful for renormalizing afterwards.

        In short: it is a list of samples. One sample is a (int, prob) tuple.

    """

    probs = np.abs(state_vec**2)  # full probability vector

    all_qbs = [k for k in range(len(state_vec.shape))]
    sum_axes = tuple([qb for qb in all_qbs if qb not in qubits])  # =~(qubits)

    probs = probs.sum(axis=sum_axes)  # tracing over unmeasured qubits.

    cumul = np.cumsum(probs)  # cumulative distribution function.

    intprob_list = []  # return object

    for _ in range(nb_samples):

        res_int = np.searchsorted(cumul, np.random.random())  # sampling

        # index computation. Needed to access probability value.
        str_bin_repr = np.binary_repr(res_int, width=len(qubits))
        index = tuple([int(s) for s in str_bin_repr])

        intprob_list.append((res_int, probs[index]))  # (int, prob) tuple

    return intprob_list


def project(state_vec, qubits, intprob):
    """
    Projects the state by assigning qubits to specified values.

    The "measure" function does not project. This is nice when asking for
    several samples. But the full behavior of a quantum state when undergoing
    measurement includes a projection onto the result state. This is what
    this function does. In practice, it is used for intermediary measurements.
    (i.e within measure and reset gates)

    Parameters
    ----------
    state_vec : :class:`numpy.ndarray`
        The state vector to project, i.e the one from which the
        results were sampled.
    qubits : :obj:`list`
        The qubits that were measured, presented as a list of integers. 
        Without this info, we don't know
        to what axes the result corresponds.
    intprob : :obj:`tuple`
        a tuple of the form (integer, probability). The integer codes
        for the value that was measured on the qubits in the list "qubits".
        The probability that the measurement had to occur. It is useful for 
        renormalizing without having to recompute a norm.

    Returns
    -------
    :class:`numpy.ndarray`
        The projected state vector. The values of the
        qubits in the "qubits" list have been assigned to the measured
        values.

    """

    all_qubits = [k for k in range(len(state_vec.shape))]  # explicit name

    state_int, prob = intprob  # result and probability there was to measure it

    index_assignment = []  # building a nd-array indexing object.

    for qb in all_qubits:
        if qb in qubits:
            val = (state_int >> qubits.index(qb)) & 1
            index_assignment.append(1 - val)  # qb = (1 - val) -> set to 0.
        else:
            index_assignment.append(slice(None))  # slice(None) = ":"

    state_vec[tuple(index_assignment)] = 0.  # actual projection
    state_vec /= np.sqrt(prob)               # renormalizing

    return state_vec


def reset(state_vec, qubits):
    """
    Resets the value of the specified qubits to 0. 

    It works by measuring each
    qubit, and then applying an X gate if the result is 1.

    for one qubit, entirely equivalent to, in AQASM:

    | MEAS q[k] c[k]
    | ?c[k] : X q[k]

    Parameters
    ----------
    state_vec: :class:`numpy.ndarray`
        nd-array containing the full state vector.    
    qubits: :obj:`list`
        list of integers, containing the qubits to reset.

    Returns
    -------
    tuple
        The function returns a tuple (state_vec, int, prob) composed of:
            - state_vec(`numpy.ndarray`) the full state vector. the specified qubits have been reset.
            - an integer: result of the measurement on the subset of qubits (when converted to binary representation, it needs to have a width of len(qubits)).
            - a float: probability the measurement had to occur.     
        
    """
    X = np.array([[0, 1], [1, 0]], dtype=np.complex128)  # X gate

    intprob_list = measure(state_vec, qubits)                # measure
    state_vec = project(state_vec, qubits, intprob_list[0])  # project
    res_int, _ = intprob_list[0]
    str_bin_repr = np.binary_repr(res_int, width=len(qubits))

    for k, res in enumerate(str_bin_repr):
        if int(res) == 1:                                   # ? c[k] : X q[k]
            state_vec = np.tensordot(X, state_vec, axes=([1], [qubits[k]]))
            state_vec = np.moveaxis(state_vec, 0, qubits[k])

    return state_vec, intprob_list[0][0], intprob_list[0][1]


def raise_break(op, op_pos, cbits):
    """
    Raises break exception, as a result of a boolean classical formula being
    evaluated to True.
    """
    exp = exceptions_types.BreakException(exceptions_types.ErrorType.BREAK)
    exp.modulename = "PYLINALG"
    exp.gate_index = op_pos

    present_cbits = []
    for i in op.formula.split(" "):
        try:
            present_cbits += [int(i)]
        except ValueError:
            pass

    exp.message = "BREAK at gate #{} : formula : {}, cbits : {}"\
        .format(op_pos, op.formula,
                [(k, bool(cbits[k])) for k in present_cbits])

    exp.cbits = [cbits[k] for k in present_cbits]

    raise exp


def mat2nparray(matrix):
    """
    Converts serialized matrix format into numpy array.

    When extracted from the quantum circuit, gate matrices are not
    directly numpy arrays. They are instances of 
    :class:`qat.comm.datamodel.Matrix`, an internally-defined structure.

    Parameters
    ----------
    matrix : :class:`qat.comm.datamodel.Matrix`
        The matrix, as extracted from circuit operation, to convert to 
        :class:`numpy.ndarray`

    Returns
    -------
    :class:`numpy.ndarray`
        returns a :class:`numpy.ndarray` of shape (2*arity,2*arity) containing
        the matrix data.

        It could directly return a :class:`numpy.ndarray` of the shape we
        use in :func:`numpy.tensordot`, but as quantum gates are typically
        represented as matrices, we kept this step.

    """

    A = np.empty((matrix.nRows, matrix.nCols), dtype=np.complex128)

    cnt = 0
    for i in range(matrix.nRows):
        for j in range(matrix.nCols):
            A[i, j] = matrix.data[cnt].re + 1j*matrix.data[cnt].im
            cnt += 1

    return A
