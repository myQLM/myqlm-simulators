# -*- coding: utf-8 -*-

"""
    Licensed to the Apache Software Foundation (ASF) under one
    or more contributor license agreements.  See the NOTICE file
    distributed with this work for additional information
    regarding copyright ownership.  The ASF licenses this file
    to you under the Apache License, Version 2.0 (the
    "License"); you may not use this file except in compliance
    with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing,
    software distributed under the License is distributed on an
    "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
    KIND, either express or implied.  See the License for the
    specific language governing permissions and limitations
    under the License.
"""

import itertools
import numpy as np

import qat.comm.shared.ttypes as shared_types
import qat.comm.datamodel.ttypes as datamodel_types
import qat.comm.exceptions.ttypes as exceptions_types
import qat.core.formula_eval as feval

from qat.core.util import extract_syntax


def get_gate_matrix(gate_definition, gate_dic):
    """
    Returns the smallest possible submatrix and the number of controls associated to a gate definition.

    Returns:
        (int, np.array)
    """
    nctrls = 0
    while gate_definition.is_ctrl or gate_definition.nbctrls:
        nctrls += gate_definition.nbctrls or 1
        gate_definition = gate_dic[gate_definition.subgate]
    return nctrls, mat2nparray(gate_definition.matrix)


def simulate(circuit):
    """
    Computes state vector at the output of provided circuit.

    State vector is stored as a :code:`numpy.ndarray`
    It is initialized at :math:`|0^n\\rangle`.
    Then, loop over gates, updating the state vector using `np.tensordot`

    Args:
        circuit (:class:`~qat.core.Circuit`): Input circuit. The
            circuit to simulate.

    Returns:
        tuple: a tuple composed of a state vector and intermediate measurements:
            - state vector: :code:`numpy.ndarray` containing the final
              state vector. It has one 2-valued index per qubits.
            - intermediate measurements: :code:`list` of :class:`qat.comm.shared.ttypes.IntermediateMeasurement`. List containing descriptors of the intermediate measurements that occurred within the circuit, so that the classical branching is known to the user.
    """
    # Initialization at |0...0>
    shape = tuple([2 for _ in range(circuit.nbqbits)])
    state_vec = np.zeros(shape, dtype=np.complex128)
    state_vec[tuple([0 for _ in range(circuit.nbqbits)])] = 1

    # cbits initilization.
    cbits = [0] * circuit.nbcbits

    interm_measurements = []
    # Loop over gates.
    for op_pos, op in enumerate(circuit):

        if op.type == datamodel_types.OpType.MEASURE:
            # measure op.qbits on state_vec and store in op.cbits
            intprob_list = measure(state_vec, op.qbits)
            state_vec = project(state_vec, op.qbits, intprob_list[0])
            res_int, prob = intprob_list[0]

            for k in range(len(op.qbits)):
                cbits[op.cbits[k]] = res_int >> (len(op.qbits) - k - 1) & 1

            interm_measurements.append(shared_types.IntermediateMeasurement(
                gate_pos=op_pos,
                cbits=[(res_int >> (len(op.qbits) - k - 1) & 1) for k in range(len(op.qbits))],
                probability=prob
            ))
            continue

        if op.type == datamodel_types.OpType.RESET:
            # measure, if result is 1 apply X.
            state_vec, res, prob = reset(state_vec, op.qbits)  # contains actual implem.
            for cb in op.cbits:
                cbits[cb] = 0
            interm_measurements.append(shared_types.IntermediateMeasurement(
                gate_pos=op_pos,
                cbits=[(res >> (len(op.qbits) - k - 1) & 1) for k in range(len(op.qbits))],
                probability=prob
            ))
            continue

        if op.type == datamodel_types.OpType.CLASSIC:
            # compute result bit of formula
            cbits[op.cbits[0]] = int(feval.evaluate(op.formula, cbits))
            continue

        if op.type == datamodel_types.OpType.BREAK:
            # evaluate formula and break if verdict is 1.
            verdict = feval.evaluate(op.formula, cbits)
            if verdict:
                raise_break(op, op_pos, cbits)
            continue

        if op.type == datamodel_types.OpType.CLASSICCTRL:
            # continue only if control cbits are all at 1.
            if not all([cbits[x] for x in op.cbits]):
                continue

        gdef = circuit.gateDic[op.gate]    # retrieving useful info.

        # Checking if the matrix has a matrix

        if not gdef.matrix:
            gname = extract_syntax(gdef, circuit.gateDic)[0]
            if gname == "STATE_PREPARATION":
                matrix = gdef.syntax.parameters[0].matrix_p
                np_matrix = mat2nparray(matrix)
                if np_matrix.shape != (2**circuit.nbqbits, 1):
                    raise exceptions_types.QPUException(code=exceptions_types.ErrorType.ILLEGAL_GATES,
                                       modulename="qat.pylinalg",
                                       file="qat/pylinalg/simulator.py",
                                       line=103,
                                       message="Gate {} has wrong shape {}, should be {}!"\
                                       .format(gname, np_matrix.shape, (2**circuit.nbqbits, 1)))
                state_vec[:] = np_matrix[:, 0].reshape(shape)
                norm = np.linalg.norm(state_vec)
                if abs(norm - 1.0) > 1e-10:
                    raise exceptions_types.QPUException(code=exceptions_types.ErrorType.ILLEGAL_GATES,
                                       modulename="qat.pylinalg",
                                       file="qat/pylinalg/simulator.py",
                                       line=103,
                                       message="State preparation should be normalized, got norm = {} instead!"\
                                       .format(norm))
                continue




        try:
            nctrls, matrix = get_gate_matrix(gdef, circuit.gateDic)
        except AttributeError as excp:
            raise exceptions_types.QPUException(code=exceptions_types.ErrorType.ILLEGAL_GATES,
                                modulename="qat.pylinalg",
                                file="qat/pylinalg/simulator.py",
                                line=103,
                                message="Gate {} has no matrix!"\
                                .format(extract_syntax(gdef, circuit.gateDic)[0])) from excp
        # Moving qubits axis in first positions
        state_vec = np.moveaxis(state_vec, op.qbits, range(len(op.qbits)))
        # Reshaping for block multiplication
        state_vec = state_vec.reshape((1 << nctrls, matrix.shape[0], 1 << (circuit.nbqbits - len(op.qbits))))
        # If controled, only applying the gate on the last block
        if nctrls:
            state_vec[-1] = np.dot(matrix, state_vec[-1])
        else:
            state_vec = np.dot(matrix, state_vec)
        # Going back to a split shape
        state_vec = state_vec.reshape(tuple(2 for _ in range(circuit.nbqbits)))
        # moving qubit back to their position
        state_vec = np.moveaxis(state_vec, range(len(op.qbits)), op.qbits)

    return state_vec, interm_measurements


def measure(state_vec, qubits, nb_samples=1):
    """
    Samples measurement results on the specified qubits.

    No projection is carried out ! See "project" function.
    Thanks to the absence of projection, several samples can be asked.

    Args:
        state_vec (numpy.ndarray): the :code:`numpy.ndarray`
            containing full state vector.
        qubits (list): list of integers specifying the subset
            of qubits to measure.
        nb_samples (int, optional): the number of samples to return. Set to 1
            by default.

    Returns:
        list: **intprob_list**, a list (of length nb_samples) containing tuples of the form (integer, probability). The integer is the result of the measurement on the subset of qubits (when converted to binary representation, it needs to have a width of len(qubits)). The probability is the probability the measurement had to occur. It is useful for renormalizing afterwards.
        In short: it is a list of samples. One sample is a (int, prob) tuple.
    """
    probs = np.abs(state_vec**2)  # full probability vector
    all_qbs = [k for k in range(len(state_vec.shape))]
    sum_axes = tuple([qb for qb in all_qbs if qb not in qubits])  # =~(qubits)
    probs = probs.sum(axis=sum_axes)  # tracing over unmeasured qubits.

    # reordering axes in the order specified by qubit list.
    cur_inds = sorted(qubits) # current probs indices

    for target, qb in enumerate(qubits): # putting indices where they should be.
        cur = cur_inds.index(qb)
        probs = probs.swapaxes(target, cur)
        cur_inds[target], cur_inds[cur] =  cur_inds[cur], cur_inds[target]

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

    Args:
        state_vec (numpy.ndarray): The state vector to project, i.e the
            one from which the results were sampled.
        qubits (list): The qubits that were measured, presented as a list
            of integers. Without this info, we don't know to what axes the result
            corresponds.
        intprob (tuple): a tuple of the form (integer, probability). The
            integer codes for the value that was measured on the qubits in the list
            "qubits". The probability that the measurement had to occur. It is
            useful for renormalizing without having to recompute a norm.

    Returns:
        numpy.ndarray: The projected state vector. The values of the qubits in the "qubits" list have been assigned to the measured values.

    """
    all_qubits = [k for k in range(len(state_vec.shape))]  # explicit name
    state_int, prob = intprob  # result and probability there was to measure it
    index_assignment = [slice(None) for _ in all_qubits]  # building a nd-array indexing object.

    for qb in qubits:
        val = (state_int >> (len(qubits) - qubits.index(qb) - 1)) & 1
        index_assignment[qb] = 1 - val      # qb = (1 - val) -> set to 0

        state_vec[tuple(index_assignment)] = 0.  # Actual projection
        index_assignment[qb] = slice(None)

    state_vec /= np.sqrt(prob)               # renormalizing
    return state_vec


def reset(state_vec, qubits):
    """Resets the value of the specified qubits to 0.

    It works by measuring each
    qubit, and then applying an X gate if the result is 1.

    for one qubit, entirely equivalent to, in AQASM:

    .. code-block:: text

        MEAS q[k] c[k]
        ?c[k] : X q[k]

    Args:
        state_vec (numpy.ndarray): nd-array containing the full state
            vector.
        qubits (list): list of integers, containing the qubits to reset.

    Returns:
        (state_vec, int, prob): a tuple composed of:
            - state_vec(`numpy.ndarray`) the full state vector. the specified qubits
              have been reset.
            - an integer: result of the measurement on the subset of qubits (when
              converted to binary representation, it needs to have a width of
              len(qubits)).
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
    present_cbits = []
    for i in op.formula.split(" "):
        try:
            present_cbits += [int(i)]
        except ValueError:
            pass
    message = "BREAK at gate #%s : formula : %s, cbits : %s"%(op_pos, op.formula,
                [(k, bool(cbits[k])) for k in present_cbits])
    exp = exceptions_types.QPUException(code=exceptions_types.ErrorType.BREAK,
                                        modulename="qat.pylinalg",
                                        message=message)

    raise exp

def compute_observable_average(state_vec, observable):
    """Directly computes an observable average from a state vector.

    For each term of the observable, the state vector is copied, tensored
    with the appropriate Pauli matrices, and scalar-producted back with the
    original state vector. The result is multiplied by the coefficient of the
    Pauli term and added to the global result.

    Args:
        state_vec (:class:`numpy.ndarray`) : The state vector, as returned
        by the "simulate" function. i.e of shape (2,...,2) with 1 index per
        qubits.

        observable (:class:`qat.core.Observable`): The observable, described
        as a coefficiented sum of Pauli products.

    Returns:
        float : The exact value of the observable average, like one would
        get by performing an infinite number of measurements of the observable
        on the state vector.
    """

    if observable.constant_coeff:
        final_value = observable.constant_coeff
    else:
        final_value = 0.

    nbqbits = len(list(state_vec.shape)) # number of qubits

    for term in observable.terms:
        local_sv = np.copy(state_vec) # local copy of the state vector

        for k, qb in enumerate(term.qbits):
        # performing tensor products with Pauli matrices of the term.
            pauli_matrix = pauli_dict[term.op[k]]

            # tensor products: exactly like gate applications in simulate func.
            local_sv = np.tensordot(pauli_matrix, local_sv, axes=([1],[qb]))
            local_sv = np.moveaxis(local_sv, [0], [qb])

        # adding to final value, with coeff.
        final_value += term.coeff * np.tensordot(state_vec.conj(), local_sv,
                                                 axes=nbqbits)

    return final_value

def mat2nparray(matrix):
    """Converts serialized matrix format into numpy array.

    When extracted from the quantum circuit, gate matrices are not
    directly numpy arrays. They are instances of
    :code:`Matrix`, an internally-defined structure.

    Args:
        matrix (:code:`qat.comm.datamodel.ttypes.Matrix`): The matrix, as extracted
            from circuit operation, to convert to :code:`numpy.ndarray`

    Returns:
        numpy.ndarray: a :code:`numpy.ndarray` of shape (2*arity,2*arity) containing
        the matrix data.

    .. notes:
        It could directly return a :code:`numpy.ndarray` of the shape we
        use in :code:`numpy.tensordot()`, but as quantum gates are typically
        represented as matrices, we kept this step.

    """
    A = np.zeros((matrix.nRows, matrix.nCols), dtype=np.complex128)
    for cnt, (i, j) in enumerate(itertools.product(range(matrix.nRows),
                                                   range(matrix.nCols))):
        A[i, j] = matrix.data[cnt].re + 1j*matrix.data[cnt].im

    return A

pauli_dict = {}
pauli_dict["X"] = np.array([[0.,1.],[1.,0.]])
pauli_dict["Y"] = np.array([[0,-1j],[1j,0]])
pauli_dict["Z"] = np.array([[1.,0.],[0.,-1.]])
