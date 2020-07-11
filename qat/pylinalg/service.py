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

import inspect
import numpy as np

from qat.comm.shared.ttypes import ProcessingType
from qat.comm.hardware.ttypes import HardwareSpecs
from qat.comm.exceptions.ttypes import ErrorType, QPUException
from qat.comm.datamodel.ttypes import ComplexNumber, OpType
from qat.core.qpu import QPUHandler
from qat.core.wrappers.result import Sample, Result, aggregate_data
from qat.core.wrappers import Circuit as WCircuit
from .simulator import simulate, measure, compute_observable_average


class PyLinalg(QPUHandler):
    """
    Simple linalg simulator plugin.

    Inherits :func:`serve` and :func:`submit` method from :class:`qat.core.qpu.QPUHandler`
    Only the :func:`submit_job` method is simulator-specific and defined here.

    """

    def __init__(self):
        super(PyLinalg, self).__init__() # calls QPUHandler __init__()

    def submit_job(self, job):
        """
        Returns a Result structure corresponding to the execution
        of a Job

        Args:
            job (:class:`~qat.core.wrappers.Job`): the job to execute

        Returns:
            :class:`~qat.core.wrappers.Result`: the result
        """
        if not isinstance(job.circuit, WCircuit):
            job.circuit = WCircuit(job.circuit)

        has_int_meas = has_intermediate_measurements(job.circuit)

        if (job.nbshots == 0) or (not has_int_meas):

            np_state_vec, interm_measurements = simulate(job.circuit)  # perform simu

        if job.qubits is not None:
            meas_qubits = job.qubits
        else:
            meas_qubits = list(range(job.circuit.nbqbits))

        all_qubits = (len(meas_qubits) == job.circuit.nbqbits)

        if not job.amp_threshold:
            job.amp_threshold = 0.0

        result = Result()
        result.meta_data = dict()
        result.raw_data = []
        if job.type == ProcessingType.SAMPLE:  # Sampling
            if job.nbshots == 0:  # Returning the full state/distribution

                if not all_qubits:
                    sum_axes = tuple(
                    [qb for qb in range(job.circuit.nbqbits) if qb not in meas_qubits])

                    # state_vec is transformed into vector of probabilities
                    np_state_vec = np.abs(np_state_vec**2)
                    np_state_vec = np_state_vec.sum(axis=sum_axes)

                # At this point axes might not be in the same order
                # as in meas_qubits: restoring this order now:

                svec_inds = sorted(meas_qubits) # current np_state_vec
                                                # indices

                for target, qb in enumerate(meas_qubits):
                    cur = svec_inds.index(qb)
                    np_state_vec = np_state_vec.swapaxes(target, cur)
                    svec_inds[target], svec_inds[cur] =  svec_inds[cur], svec_inds[target]

                # loop over states. val is amp if all_qubits else prob
                for int_state, val in enumerate(np_state_vec.ravel()):
                    amplitude = None  # in case not all qubits
                    if all_qubits:
                        amplitude = ComplexNumber(re=val.real, im=val.imag)
                        prob = np.abs(val)**2
                    else:
                        prob = val

                    if prob <= job.amp_threshold**2:
                        continue

                    sample = Sample(state=int_state,
                                    amplitude=amplitude,
                                    probability=prob,
                                    intermediate_measurements=interm_measurements)

                    # append
                    result.raw_data.append(sample)

            elif job.nbshots > 0:  # Performing shots

                if has_int_meas:
                # if intermediate measurements, the entire simulation must
                # be redone for every shot. Because the intermediate measurements
                # might change the output distribution probability.

                    intprob_list = []
                    interm_meas_list = []
                    for _ in range(job.nbshots):
                        np_state_vec, interm_measurements = simulate(job.circuit)
                                                            # perform simu
                        intprob = measure(np_state_vec,
                                           meas_qubits,
                                           nb_samples=1)

                        intprob_list.append(intprob[0])
                        interm_meas_list.append(interm_measurements)

                else:
                # no need to redo the simulation entirely. Just sampling.

                    intprob_list = measure(np_state_vec,
                                           meas_qubits,
                                           nb_samples=job.nbshots)

                    interm_meas_list = [[] for _ in range(job.nbshots)]

                # convert to good format and put in container.
                for k, intprob in enumerate(intprob_list):

                    res_int, prob = intprob

                    amplitude = None  # in case not all qubits
                    if all_qubits:
                        # accessing amplitude of result
                        indices = [res_int >> k & 1
                                   for k in range(len(meas_qubits))]
                        indices.reverse()

                        amp = np_state_vec[tuple(indices)]
                        amplitude = ComplexNumber(re=amp.real, im=amp.imag)

                    # final result object
                    sample = Sample(state=res_int,
                            intermediate_measurements=interm_meas_list[k])
                    # append
                    result.raw_data.append(sample)

                if job.aggregate_data:
                    result = aggregate_data(result)

            else:
                raise QPUException(ErrorType.INVALID_ARGS,
                                   "qat.pylinalg",
                                   "Invalid number of shots %s"% job.nbshots)

            return result


        if job.type == ProcessingType.OBSERVABLE:

            result.value = compute_observable_average(np_state_vec, 
                                                      job.observable)

            return result

        raise QPUException(ErrorType.INVALID_ARGS,
                           "qat.pylinalg",
                           "Unsupported job type %s"%job.type)

def has_intermediate_measurements(circuit):
    """
    Simple utility function.

    Args:
        circuit (Circuit): a circuit
    Returns:
        bool: True if circuit contains intermediate measurements
    """
    for op in circuit.ops:
        if op.type == OpType.MEASURE or  op.type == OpType.RESET:
            return True
    return False

get_qpu_server = PyLinalg
