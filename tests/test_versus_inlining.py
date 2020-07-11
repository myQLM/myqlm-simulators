# -*- coding : utf-8 -*-

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
