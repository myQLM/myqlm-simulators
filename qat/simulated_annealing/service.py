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
from qat.comm.exceptions.ttypes import ErrorType, QPUException
from qat.core.qpu import QPUHandler
from qat.core.spins import spins_to_integer
from qat.core.variables import ArithExpression
from qat.core.wrappers.result import Sample, Result, aggregate_data
from qat.lang.AQASM.bits import QRegister


class SimulatedAnnealing(QPUHandler):
    """
    A Simulated Annealing solver interfaced as a Quantum Processing Unit (QPU)

    Args:
        temp_t (:class:`~qat.core.variables.ArithExpression`): temperature-time dependence. It needs to be specified using
            a variable :code:`t` instantiated with the class :class:`~qat.core.Variable`.
        n_steps (int): number of annealing time steps in Temp(t) evolution.
        seed (int, optional): Randomness seed.
    """

    def __init__(self, temp_t, n_steps, seed=None):

        # Check that the temp_t is given, of the right type and containing
        # only one Variable, which is 't'.
        error_message = ("The temperature function should be specified with "
                         "a variable 't', defined using the qat.core.Variable "
                         "class. For example 't = Variable(\"t\", float)'.")
        if temp_t is None:
            raise ValueError(error_message)

        if not isinstance(temp_t, ArithExpression):
            raise TypeError(error_message)

        variables = temp_t.get_variables()
        variables_list = list(variables)
        if len(variables_list) != 1 or variables_list[0] != 't':
            raise TypeError(error_message)

        # If no errors were detected, assign temp_t
        self.temp_t = temp_t

        # Check if a positive n_steps was given
        if n_steps is None:
            raise ValueError("The number of steps should be specified and as a positive integer.")
        else:
            if n_steps < 0:
                raise ValueError("The number of steps should be specified and as a positive integer.")
        self.n_steps = n_steps

        # Check if a positive seed was given
        if seed is not None:
            if seed < 0:
                raise ValueError("Please use a positive integer seed.")
        self.seed = seed

        super(SimulatedAnnealing, self).__init__() # calls QPUHandler __init__()

    def submit_job(self, job):
        """
        Execute simulated annealing for a given job.

        Args:
            job (:class:`~qat.core.Job`): the job to execute

        Returns:
            result (:class:`~qat.core.Result`): a result with the solution spin configuration(s)
        """

        # Check if an observable is present and one can extract the Ising tuple from it.
        if job.type == ProcessingType.OBSERVABLE:
            raise QPUException(ErrorType.INVALID_ARGS,
                                                'qat.simulated_annealing',
                                                "invalid job type, only accepting SAMPLE")

        if job.schedule is None:
            raise QPUException(ErrorType.INVALID_ARGS,
                               modulename='qat.simulated_annealing',
                               message="invalid job, only accepting Schedules")

#         if job.schedule.gamma_t is not None:
#             raise QPUException(ErrorType.INVALID_ARGS,
#                                'qat.simulated_annealing',
#                                "An SA QPU was called, but the job contains gamma_t, "
#                                "which can only be used with an SQA solver, available "
#                                "in the full QLM.")

        drive = job.schedule.drive
        if job.schedule.drive is None:
            raise QPUException(ErrorType.INVALID_ARGS,
                               'qat.simulated_annealing',
                               "no drive detected, which should contain an Ising observable.")

        if len(drive) != 1 or drive[0][0] != 1:
            raise QPUException(ErrorType.INVALID_ARGS,
                               'qat.simulated_annealing',
                               "the drive should contain only one Observable with "
                               "an Ising tuple and coefficient 1.")

        # Extract the Ising parameters and tmax
        J_coupling, h_mag, offset = extract_j_and_h_from_obs(drive[0][1])
        tmax = job.schedule.tmax

        # Specify the list of annealing times
        time_list = np.linspace(0, tmax, int(self.n_steps))

        # Produce the temperatures at the annealing times
        if "Expression" in str(type(self.temp_t)):
            temp_list = [self.temp_t(t=t) for t in time_list]
        else:
            temp_list = [self.temp_t for t in time_list]

        # Will appeand QRegister to the result for proper dealing with the states
        qreg = QRegister(0, length=job.schedule.nbqbits)

        # Now give all the annealing parameters to the sa solver and get an answer
        sample_list = []
        for shot in range(job.nbshots):

            solution_configuration = self.sa(J_coupling, h_mag, temp_list)

            state_int = spins_to_integer(solution_configuration)
            sample_list.append(Sample(state=state_int))

        result = Result(raw_data=sample_list,
                        qregs=[qreg],
                        meta_data=dict())
        
        if job.aggregate_data:
            result = aggregate_data(result)

        return result

    def sa(self, J_coupling, h_mag, temp_list):
        """
        The algorithm implementing simulated annealing.
        
        Args:
            J (2D numpy array): an array with the coupling between each two spins - it represents
              the :math:`J` matrix from the Hamiltonian of the problem
            h (1D numpy array): an array with the magnetic field acting on each of the spins,
              coming from the Hamiltonian of the problem
            temp_t (:class:`~qat.core.variables.ArithExpression`): temperature-time dependence. It needs to be specified using
              a variable :code:`t` instantiated with the class :class:`~qat.core.Variable`.
              
        Returns:
            1D numpy array: an array representing the solution spin configuration after the simulated annealing
        """

        if self.seed is not None:
            np.random.seed(self.seed)

        n_spins = len(h_mag)
        assert len(J_coupling) == n_spins

        spin_conf = np.random.choice([1, -1], n_spins)
        local_h = h_mag + J_coupling @ spin_conf
        for temp in temp_list:
            for spin in range(n_spins):
                delta_E = 2.0 * spin_conf[spin] * local_h[spin]
                flip_prob = 1.0 if (delta_E < 0) else np.exp(-delta_E / temp)
                if (np.random.rand() < flip_prob):
                    local_h -= 2 * spin_conf[spin] * J_coupling[spin, :]
                    spin_conf[spin] *= -1

        return spin_conf 


def extract_j_and_h_from_obs(obs):
    r"""
    A function to extract the :math:`J` coupling matrix, magnetic field
    :math:`h` and Ising energy offset :math:`E_I` from the Hamiltonian of an Ising 
    problem. The Hamiltonian should be of the form

    .. math::

        H = - \sum_{ij} J_{ij} s_i s_j - \sum_i h_i s_i - E_I

    with :math:`s_i, s_j \in \{-1,1\}`.

    Args:
        obs (:class:`~qat.core.Observable`): an observable for an Ising problem

    Returns:
        3-element tuple containing

        - **J** (*2D numpy array*) - an array with the coupling between each two spins - it
          represents the :math:`J` matrix from the Hamiltonian of the problem
        - **h** (*1D numpy array*) - an array with the magnetic field acting on each of the
          spins, coming from the Hamiltonian of the problem
        - **offset_i** (*double*) - the value of the Ising offset energy in the respective
          Hamiltonian
    """
    # The matrices of the observable defined in Ising representation should be retrieved directly from _ising
    if obs._ising is not None:
        return obs._ising.get_j_h_and_offset()

    nqbits = obs.nbqbits
    h_mag = np.zeros(nqbits)
    J_coupling = np.zeros((nqbits, nqbits))

    for term in obs.terms:
        if len(term.qbits) == 1:
            assert(term.op == "Z")
            h_mag[term.qbits[0]] = -term.coeff
        elif len(term.qbits) == 2:
            assert(term.op == "ZZ")
            J_coupling[term.qbits[0], term.qbits[1]] = -term.coeff
        else:
            current_line_no = inspect.stack()[0][2]
            raise QPUException(ErrorType.INVALID_ARGS,
                               modulename='qat.simulated_annealing',
                               message="invalid target Hamiltonian, only "
                                       "accepting terms of type 'Z' or 'ZZ', "
                                       "got %s instead" % term)

    return 1.0 * (J_coupling + J_coupling.T), h_mag, -obs.constant_coeff
