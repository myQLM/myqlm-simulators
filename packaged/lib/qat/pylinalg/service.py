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
import qat.comm.qproc.ttypes as simu_types
import qat.core.qproc as qproc
#from bitstring import BitArray as OrigBitArray
from qat.core.simutil import rev_bits
#from .stochastic_util import replace_noises

CURRENT_EXECUTION_KEY = None
RHO_DIAG = None
ERR_RHO_DIAG = None
MEASURE_WORKER = None
HISTORY = []
CBITS = None
STOPPED_BECAUSE_FULL_BUFFER = None
_EXEC_COUNT = 0 #number of executions of circuit evolution


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
            simu_input (`Circuit <datamodel.html#Struct_Circuit>`_.): simulation input information
        """
        logging.info("New simulation")

        if simu_input.options.mode == simu_types.Mode.DEFAULT:
            logging.info("Mode DEFAULT")
        elif simu_input.options.mode == simu_types.Mode.ANALYZE:
            logging.info("Mode ANALYZE")
        else:
            raise task_types.InvalidArgumentException(0,
                                                      "qat.pylinalg",
                                                      "Unknown execution mode %s"
                                                      % simu_input.options.mode)

        ret_val = simu_types.StateVector()

        if simu_input.options.mode == simu_types.Mode.ANALYZE:
            logging.info("Analyze mode")

            # Implementation goes here.

        elif simu_input.options.mode == simu_types.Mode.DEFAULT:
            # Sample states for a given density matrix
            logging.info("Default mode")

            print("sucessfully called submit in default mode")

            # Implementation goes here.

        else:
            raise task_types.InvalidArgumentException(0, "qat.pylinalg",
                      "Unknown execution mode %s" % simu_input.options.mode)

        logging.info("End of simulation")

        return ret_val

