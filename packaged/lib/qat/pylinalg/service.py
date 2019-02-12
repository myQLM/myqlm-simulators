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
from datetime import datetime
import numpy as np

import bxi.base.log as logging
import qat.comm.task.ttypes as task_types
import qat.comm.qpu.ttypes as qpu_types
import qat.comm.datamodel.ttypes as datamodel_types
import qat.comm.qproc.ttypes as simu_types
import qat.core.qproc as qproc
import qat.core.simutil as core_simutil

#from bitstring import BitArray as OrigBitArray

from qat.pylinalg import simulator as np_engine

#CURRENT_EXECUTION_KEY = None
#HISTORY = []
#CBITS = None
#STOPPED_BECAUSE_FULL_BUFFER = None
#_EXEC_COUNT = 0 #number of executions of circuit evolution


class PyLinalg(qproc.Plugin):
    """
    Simple linalg simulator plugin.
    """

    def __init__(self, **kwargs):

        self._circuit_key = None

        super(PyLinalg, self).__init__(**kwargs)

    @classmethod
    def addargs(cls, parser):
        """Define arguments for command-line usage"""
        pass

    def Type(self):
        return task_types.QPU()

    def Submit(self, simu_input):
        """
            Execute the simulation

        Args:
            simu_input (`Circuit <datamodel.html#Struct_Circuit>`_.): 
                                                simulation input information
        """

        logging.info("New simulation")

        qproc_state_vec = simu_types.StateVector()
        qproc_state_vec.states = [] # container: stores final states
                                    # in both DEFAULT and ANALYZE
            
        circ = simu_input.task.circuit # shorter

        np_state_vec, history = np_engine.simulate(circ) # perform simu

       # if no qubits specified then measure all.
        if simu_input.options.qbits:
            meas_qubits = simu_input.options.qbits
        else:
            meas_qubits = [k for k in range(circ.nbqbits)]

        # for simpler handling of subset-of-qubits case.
        all_qubits = False
        if len(meas_qubits) == circ.nbqbits:
            all_qubits = True

       # that's a big if. 
        if simu_input.options.mode == simu_types.Mode.ANALYZE:
            logging.info("Analyze mode")

            if simu_input.options.range.last_state:
                return qproc_state_vec

            # trace over un-measured qubits
            if not all_qubits:
            
                all_qb = range(circ.nbqbits) # shorter
                sum_axes = tuple(qb for qb in all_qb if qb not in meas_qubits)

                # state_vec is transformed into vector of PROBABILITIES
                np_state_vec = np.abs(np_state_vec**2) 
                np_state_vec = np_state_vec.sum(axis=sum_axes) 

            # setting up threshold
            threshold = 0.0
            if simu_input.options.threshold is not None:
                threshold = simu_input.options.threshold

            # loop over states. val is amp if all_qubits else prob
            for int_state, val in enumerate(np_state_vec.ravel()):
    
                amplitude = None # in case not all qubits
                if all_qubits:
                    
                    amplitude = datamodel_types.ComplexNumber()
                    amplitude.re = val.real
                    amplitude.im = val.imag     
                    prob = abs(val**2)

                else:
                    prob = val

                if prob <= threshold:
                    continue

                # byte conversion
                int_state = core_simutil.rev_bits(int_state, len(meas_qubits))
                bytes_state = int_state.to_bytes((int_state.bit_length() // 8) + 1,
                                                byteorder="little")    
 
                # final result object
                qpu_result = qpu_types.Result(bytes_state, 
                                                probability=prob,
                                                amplitude=amplitude)

                # append
                qproc_state_vec.states.append(qpu_result)
    
        elif simu_input.options.mode == simu_types.Mode.DEFAULT:
            logging.info("Default mode")

            # measure: 
            intprob_list = np_engine.measure(np_state_vec, 
                                         meas_qubits,
                                         nb_samples=simu_input.options.run_nb)

            # convert to good format and put in container.
            for res_int, prob in intprob_list:

                amplitude = None # in case not all qubits
                if all_qubits:
                    # accessing amplitude of result
                    indices = [] 
                    for k in range(len(meas_qubits)):
                        indices.append(res_int >> k & 1)
                    indices.reverse()
         
                    amplitude = datamodel_types.ComplexNumber()
                    amplitude.re = np_state_vec[tuple(indices)].real # access
                    amplitude.im = np_state_vec[tuple(indices)].imag # access

                # byte conversion
                res_int = core_simutil.rev_bits(res_int, len(meas_qubits))
                bytes_state = res_int.to_bytes((res_int.bit_length() // 8) + 1,
                                                byteorder="little")    
 
                # final result object
                qpu_result = qpu_types.Result(bytes_state, 
                                                probability=prob,
                                                amplitude=amplitude)

                # append
                qproc_state_vec.states.append(qpu_result)

        else:
            raise task_types.InvalidArgumentException(0, "qat.pylinalg",
                      "Unknown execution mode %s" % simu_input.options.mode)

        logging.info("End of simulation")

        return qproc_state_vec

