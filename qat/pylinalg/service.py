# -*- coding: utf-8 -*-
"""
@authors Bertrand Marchand
@brief pylinalg simulator service
@copyright 2019  Bull S.A.S.  -  All rights reserved.\n
           This is not Free or Open Source software.\n
           Please contact Bull SAS for details about its license.\n
           Bull - Rue Jean Jaurès - B.P. 68 - 78340 Les Clayes-sous-Bois
@namespace qat.pylinalg
"""
import inspect
import numpy as np

from qat.comm.shared.ttypes import Sample, Result, ProcessingType
from qat.comm.hardware.ttypes import HardwareSpecs
from qat.comm.exceptions.ttypes import ErrorType, QPUException
from qat.comm.datamodel.ttypes import ComplexNumber
from qat.core.qpu import QPUHandler
from qat.core.wrappers.result import aggregate_data
from qat.core.wrappers import Circuit as WCircuit
from .simulator import simulate, measure


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
        np_state_vec, interm_measurements = simulate(job.circuit)  # perform simu

        if job.qubits is not None:
            meas_qubits = job.qubits
        else:
            meas_qubits = list(range(job.circuit.nbqbits))

        all_qubits = (len(meas_qubits) == job.circuit.nbqbits)

        if not job.amp_threshold:
            job.amp_threshold = 0.0

        result = Result()
        result.raw_data = []
        if job.type == ProcessingType.SAMPLE:  # Sampling
            if job.nbshots == 0:  # Returning the full state/distribution
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
                intprob_list = measure(np_state_vec,
                                       meas_qubits,
                                       nb_samples=job.nbshots)

                # convert to good format and put in container.
                for res_int, prob in intprob_list:

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
                                    intermediate_measurements=interm_measurements)
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
            current_line_no = inspect.stack()[0][2]
            raise QPUException(code=ErrorType.INVALID_ARGS,
                               modulename="qat.pylinalg",
                               message="Unsupported job type OBSERVABLE",
                               file=__file__,
                               line=current_line_no)

        raise QPUException(ErrorType.INVALID_ARGS,
                           "qat.pylinalg",
                           "Unsupported job type %s"%job.type)


get_qpu_server = PyLinalg
