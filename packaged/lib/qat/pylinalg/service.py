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
import numpy as np

import inspect

from qat.core.qpu import QPUHandler
import qat.core.simutil as core_simutil

from qat.comm.shared.ttypes import Sample, Result, ProcessingType
from qat.comm.hardware.ttypes import HardwareSpecs
from qat.comm.exceptions.ttypes import RuntimeException, ErrorType, InvalidArgumentException
import qat.comm.datamodel.ttypes as datamodel_types
from qat.pylinalg import simulator as np_engine


class PyLinalg(QPUHandler):
    """
    Simple linalg simulator plugin.

    Inherits :func:`serve` and :func:`submit` method from :class:`qat.core.qpu.QPUHandler`
    Only the :func:`submit_job` method is simulator-specific and defined here.
     
    """

    def __init__(self):
        super(PyLinalg, self).__init__() # calls QPUHandler __init__()
        self._circuit_key = None

    def submit_job(self, job):
        """
        Returns a Result structure corresponding to the execution
        of a Job

        Args:
            job (:class:`~qat.core.wrappers.Job`): the job to execute

        Returns:
            :class:`~qat.core.wrappers.Result`: the result
        """
        circ = job.circuit
        np_state_vec, history = np_engine.simulate(circ)  # perform simu

        if job.qubits is not None:
            meas_qubits = job.qubits
        else:
            meas_qubits = [k for k in range(circ.nbqbits)]

        all_qubits = (len(meas_qubits) == circ.nbqbits)

        result = Result()
        result.raw_data = []
        if job.type == ProcessingType.OBSERVABLE:
            current_line_no = inspect.stack()[0][2]
            raise RuntimeException(code=ErrorType.INVALID_ARGS,
                                   modulename="qat.pylinalg",
                                   message="Unsupported sampling type",
                                   file=__file__,
                                   line=current_line_no)

        if job.type == ProcessingType.SAMPLE:  # Sampling
            if job.nbshots == 0:  # Returning the full state/distribution
                if not all_qubits:
                    all_qb = range(circ.nbqbits)  # shorter
                    sum_axes = tuple(
                        [qb for qb in all_qb if qb not in meas_qubits])

                    # state_vec is transformed into vector of PROBABILITIES
                    np_state_vec = np.abs(np_state_vec**2)
                    np_state_vec = np_state_vec.sum(axis=sum_axes)

                # setting up threshold NOT IMPLEMENTED! DUMMY VALUE!
                threshold = 1e-12

                # loop over states. val is amp if all_qubits else prob
                for int_state, val in enumerate(np_state_vec.ravel()):
                    amplitude = None  # in case not all qubits
                    if all_qubits:
                        amplitude = datamodel_types.ComplexNumber()
                        amplitude.re = val.real
                        amplitude.im = val.imag
                        prob = np.abs(val)**2
                    else:
                        prob = val

                    if prob <= threshold:
                        continue

                    sample = Sample(state=int_state,
                                    amplitude=amplitude,
                                    probability=prob,
                                    intermediate_measures=history)

                    # append
                    result.raw_data.append(sample)

            elif job.nbshots>0:  # Performing shots
                intprob_list = np_engine.measure(np_state_vec,
                                                 meas_qubits,
                                                 nb_samples=job.nbshots)

                # convert to good format and put in container.
                for res_int, prob in intprob_list:

                    amplitude = None  # in case not all qubits
                    if all_qubits:
                        # accessing amplitude of result
                        indices = []
                        for k in range(len(meas_qubits)):
                            indices.append(res_int >> k & 1)
                        indices.reverse()

                        amplitude = datamodel_types.ComplexNumber()
                        amplitude.re = np_state_vec[tuple(
                            indices)].real  # access
                        amplitude.im = np_state_vec[tuple(
                            indices)].imag  # access

                    # final result object
                    sample = Sample(state=res_int,
                                    probability=prob,
                                    amplitude=amplitude,
                                    intermediate_measures=history)
                    # append
                    result.raw_data.append(sample)
            else:
                raise InvalidArgumentException(0, "qat.pylinalg",
                                               "Invalid number of shots %s"
                                               % job.nbshots)

            return result
        raise NotImplementedError


get_qpu_server = PyLinalg
