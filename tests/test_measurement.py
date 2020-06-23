# -*- coding: utf-8 -*-

"""
@authors    Arnaud Gazda <arnaud.gazda@atos.net>
@copyright  2020 Bull S.A.S. - All rights reserved
            This is not Free or Open Source software.
            Please contact Bull SAS for details about its license.
            Bull - Rue Jean Jaurès - B.P. 68 - 78340 Les Clayes-sous-Bois

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
    prog.cc_apply(cbits[0], Z, bell_pair[1])
    prog.cc_apply(cbits[1], X, bell_pair[1])

    # Return circuit
    return prog.to_circ()


def test_teleportation():
    """
    Checks the output of the teleportation
    """
    # Generate two circuits
    for circ in [generate_teleportation(True), generate_teleportation(False)]:
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
                assert sample.amplitude == pytest.approx(amplitude_one) or \
                        sample.amplitude == pytest.approx(-amplitude_one)

            # If last qubit is 0
            else:
                assert sample.amplitude == pytest.approx(amplitude_zero) or \
                        sample.amplitude == pytest.approx(-amplitude_zero)
