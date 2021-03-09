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

"""
Description: Unit test for the PyLinalg simulator
             This test checks intermediate measurements
"""

import pytest
from qat.lang.AQASM import Program, RX, RZ, CNOT, H, Z, X
from qat.qpus import PyLinalg


def generate_teleportation(split_measures: bool):
    """
    Generates a circuit corresponding to the teleportation
    circuit

    Args:
        split_measures (bool): split measures

    Returns:
        :class:`~qat.core.Circuit`: generated circuit
    """
    # Init program
    prog = Program()
    source = prog.qalloc(1)
    bell_pair = prog.qalloc(2)
    cbits = prog.calloc(2)

    # Init source qubit
    prog.apply(RX(1.23), source)
    prog.apply(RZ(4.56), source)

    # Init Bell pair
    prog.apply(H, bell_pair[0])
    prog.apply(CNOT, bell_pair)

    # Bell pair measurement between source qubit and bell_pair[0]
    prog.apply(CNOT, source, bell_pair[0])
    prog.apply(H, source)

    if split_measures:
        prog.measure(source[0], cbits[0])
        prog.measure(bell_pair[0], cbits[1])

    else:
        prog.measure([source[0], bell_pair[0]], cbits)

    # Classic control
    prog.cc_apply(cbits[1], X, bell_pair[1])
    prog.cc_apply(cbits[0], Z, bell_pair[1])

    # Return circuit
    return prog.to_circ()


def test_teleportation():
    """
    Checks the output of the teleportation
    """
    # Generate two circuits
    for circ in [generate_teleportation(True), generate_teleportation(False)] * 10:
        # Submit teleportation circuit to PyLinalg
        result = PyLinalg().submit(circ.to_job())

        # Init expected result
        amplitude_zero = -0.5319070945531361-0.6198336118074692j
        amplitude_one = 0.4378426919829602+0.3757325026063933j

        # Check result
        assert len(result) == 2

        for sample in result:
            # If last qubit is 1
            if sample.state.int & 1:
                assert sample.amplitude == pytest.approx(amplitude_one)

            # If last qubit is 0
            else:
                assert sample.amplitude == pytest.approx(amplitude_zero)


def test_multiple_measurements():
    """
    Submit a circuit composed to 2 intermediate measurements
    """
    # Build a program
    prog = Program()
    qbits = prog.qalloc(2)
    cbits = prog.calloc(2)
    prog.apply(X, qbits[0])
    prog.measure(qbits, cbits)
    prog.apply(CNOT, qbits)
    prog.measure(qbits, cbits)

    circ = prog.to_circ()

    # Submit circuit
    result = PyLinalg().submit(circ.to_job())

    # Check result
    assert len(result) == 1
    sample = result.raw_data[0]
    assert sample.state.int == 3

    # Check intermediate measurements
    assert len(sample.intermediate_measurements) == 2
    assert sample.intermediate_measurements[0].cbits == [True, False]
    assert sample.intermediate_measurements[1].cbits == [True, True]


def test_reset():
    """
    Check the reset gate
    """
    # Define a program
    prog = Program()
    qbits = prog.qalloc(2)
    prog.apply(X, qbits[0])
    prog.reset(qbits)
    circ = prog.to_circ()

    # Submit circuit
    result = PyLinalg().submit(circ.to_job())

    # Check result
    assert len(result) == 1
    sample = result.raw_data[0]
    assert sample.state.int == 0

    # Check intermediate measurements
    assert len(sample.intermediate_measurements) == 1
    print(sample.intermediate_measurements)
    assert sample.intermediate_measurements[0].cbits == [True, False]
