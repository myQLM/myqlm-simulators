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

"""
Unit tests for simulated annealing and its functions
"""

import pytest
import unittest
import numpy as np
import networkx as nx
from qat.opt import MaxCut
from qat.qpus import SimulatedAnnealing
from qat.core import Job, Observable, Schedule, Result, Variable, Term
from qat.simulated_annealing.service import spins_to_integer, integer_to_spins, \
    extract_j_and_h_from_obs
import qat.comm.exceptions.ttypes as exceptions_types

def get_observable(J, h, offset):
    """
    Returns an Observable from a J coupling and magnetic field h
    of an Ising problem.

    Returns:
        :class:`~qat.core.Observable`: an Ising Hamiltonian encoding the problem
    """

    n_spins = J.shape[0]
    observable = Observable(n_spins, constant_coeff=-offset)
    for i in range(n_spins):
        if not np.isclose(h[i], 0):
            observable.terms.append(Term(-h[i], "Z", [i]))
        for j in range(i + 1, n_spins):
            if not np.isclose(J[i, j], 0):
                observable.terms.append(Term(-J[i, j], "ZZ", [i, j]))
    return observable


class TestSimulatedAnnealing(unittest.TestCase):
    
    # Create a valid J, h and offset
    J_random = np.random.rand(200, 200)
    J_not_symmetric = J_random - np.diag(np.diag(J_random))
    J_valid = (J_not_symmetric + J_not_symmetric.T) / 2

    h = np.random.rand(5)
    h_valid = np.random.rand(len(J_valid[0]))

    offset_valid = np.random.rand() * 1000
        
    # Create a valid temperature function
    t = Variable("t", float)
    temp_t_valid = t**3 + 8 * t + 1
#     temp_t_valid = 2 * (1 - t) +  0.01 * t

    # Invalid temp_t
    t = Variable("p", float)
    temp_t_invalid_1 = 31 * t**2 + 7

    # Another invalid temp_t
    t = Variable("t", float)
    q = Variable("q", float)
    temp_t_invalid_2 = 15 * t**2 - 8 * q

    # And for the number of steps
    n_steps_invalid = -200
    n_steps_valid = 5000

    # Create an actual problem
    problem = MaxCut(nx.full_rary_tree(5, 77))

    # Prepare a Job for this problem
    job_valid = problem.to_job()

    def test_creation(self):
        # Check that no exception is raised
        qpu = SimulatedAnnealing(temp_t=TestSimulatedAnnealing.temp_t_valid,
                                 n_steps=TestSimulatedAnnealing.n_steps_valid)

        # Now check if the proper exceptions are raised - temp_t
        with pytest.raises(ValueError):
            assert qpu == SimulatedAnnealing(temp_t=None,
                                             n_steps=TestSimulatedAnnealing.n_steps_valid)
        with pytest.raises(TypeError):
            assert qpu == SimulatedAnnealing(temp_t=TestSimulatedAnnealing.temp_t_invalid_1,
                                             n_steps=TestSimulatedAnnealing.n_steps_valid)
        with pytest.raises(TypeError):
            assert qpu == SimulatedAnnealing(temp_t=TestSimulatedAnnealing.temp_t_invalid_2,
                                             n_steps=TestSimulatedAnnealing.n_steps_valid)

        # Check the exceptions for the number of annealing steps
        with pytest.raises(ValueError):
            assert qpu == SimulatedAnnealing(temp_t=TestSimulatedAnnealing.temp_t_valid,
                                             n_steps=None)
        with pytest.raises(ValueError):
            assert qpu == SimulatedAnnealing(temp_t=TestSimulatedAnnealing.temp_t_valid,
                                             n_steps=TestSimulatedAnnealing.n_steps_invalid)

        # And a check for the exception raised by negative number of seeds
        with pytest.raises(ValueError):
            assert qpu == SimulatedAnnealing(temp_t=TestSimulatedAnnealing.temp_t_valid,
                                 n_steps=TestSimulatedAnnealing.n_steps_valid,
                                 seed=-1298)

    def test_submit_job(self):

        # Create a valid qpu
        qpu_valid = SimulatedAnnealing(temp_t=TestSimulatedAnnealing.temp_t_valid,
                                       n_steps=TestSimulatedAnnealing.n_steps_valid,
                                       seed=8017)

        # Create an Observable Job and check that such Jobs are not dealt with by the qpu
        observable = Observable(5)
        job = Job(observable=observable)
        with pytest.raises(exceptions_types.QPUException):
            assert result == qpu_valid.submit_job(job)

        # Create a circuit Job a and check that such Jobs are not dealt with by the qpu
        from qat.lang.AQASM import Program, H
        prog = Program()
        reg = prog.qalloc(1)
        prog.apply(H, reg)
        prog.reset(reg)
        with pytest.raises(exceptions_types.QPUException):
            assert result == qpu_valid.submit(prog.to_circ().to_job(nbshots=1))

        # Create a Job from a Schedule with empty drive and check that such
        # Jobs are not dealt with by the qpu
        schedule = Schedule()
        job = Job(schedule=schedule)
        with pytest.raises(exceptions_types.QPUException):
            assert result == qpu_valid.submit_job(job)

        # Create a job from a Schedule with a drive with more than one observable
        # or an observable with coefficient not 1 to check that such Jobs don't work
        # with the qpu
        observable = get_observable(TestSimulatedAnnealing.J_valid,
                                    TestSimulatedAnnealing.h_valid,
                                    TestSimulatedAnnealing.offset_valid)
        drive_invalid_1 = [(1, observable), (1, observable)]
        schedule = Schedule(drive=drive_invalid_1)
        job = schedule.to_job()
        with pytest.raises(exceptions_types.QPUException):
            assert result == qpu_valid.submit_job(job)
        drive_invalid_2 = [(5, observable)]
        schedule = Schedule(drive=drive_invalid_2)
        job = schedule.to_job()
        with pytest.raises(exceptions_types.QPUException):
            assert result == qpu_valid.submit_job(job)

        # Solve the problem and check that the returned result is Result
        result = qpu_valid.submit_job(TestSimulatedAnnealing.job_valid)
        assert isinstance(result, Result)

    def test_spins_to_integer_and_back_translations(self):
        """
        Tests if the respective two methods in service.py translate
        backwards and forwards properly
        """

        random_spin_config = np.random.randint(2, size=10) * 2 - 1
        random_spin_config_size = len(random_spin_config)
        random_spin_config_to_int = spins_to_integer(random_spin_config)
        translated_spin_config = integer_to_spins(random_spin_config_to_int, random_spin_config_size)
        translated_int = spins_to_integer(translated_spin_config)

        assert np.array_equal(random_spin_config, translated_spin_config)
        assert random_spin_config_to_int == translated_int

    def test_extract_j_and_h_from_obs(self):
        """
        Tests if the J coupling and h magnetic field are properly
        extracted from an observable.
        First creates an observable for some given J and h, then
        extracts the J and h, then compars with the inital ones.
        """

        # Create an Observable and use the tested method to get back J, h and the offset
        observable = get_observable(TestSimulatedAnnealing.J_valid,
                                    TestSimulatedAnnealing.h_valid,
                                    TestSimulatedAnnealing.offset_valid)
        J_extracted, h_extracted, offset_extracted = extract_j_and_h_from_obs(observable)

        assert np.array_equal(TestSimulatedAnnealing.J_valid, J_extracted)
        assert np.array_equal(TestSimulatedAnnealing.h_valid, h_extracted)
        assert TestSimulatedAnnealing.offset_valid == offset_extracted


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
