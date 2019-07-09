# -*- coding : utf-8 -*-
"""
@authors Simon Martiel <simon.martiel@atos.net>
@internal
@copyright 2017-2019  Bull S.A.S.  -  All rights reserved.
           This is not Free or Open Source software.
           Please contact Bull SAS for details about its license.
           Bull - Rue Jean Jaurès - B.P. 68 - 78340 Les Clayes-sous-Bois

@file qat-mps/tests/test_versus_inlining.py
@brief
@namespace qat-mps.tests.test_versus_inlining
"""
import unittest
import numpy as np

from qat.lang.AQASM import *
from qat.lang.AQASM.qftarith import QFT

from qat.pylinalg import PyLinalg

from qat.core.simutil import wavefunction


class TestVsInlining(unittest.TestCase):
    """
    Testing the simulation of compressed circuits.
    """
    def test_qft(self):
        """ Testing simulation of inlined/not-inlined QFT """
        prog = Program()
        qbits = prog.qalloc(5)
        prog.apply(QFT(5), qbits)
        circuit_default = prog.to_circ()
        circuit_inlined = prog.to_circ(inline=True)

        qpu = PyLinalg()

        psi_d = wavefunction(circuit_default, qpu)
        psi_i = wavefunction(circuit_inlined, qpu)

        self.assertAlmostEqual(np.linalg.norm(psi_d - psi_i), 0.)
