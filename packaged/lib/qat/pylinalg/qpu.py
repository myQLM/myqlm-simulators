# -*- coding: utf-8 -*-
"""
@authors Jean-Noël Quintin <jean-noel.quintin@bull.net>
@copyright 2017  Bull S.A.S.  -  All rights reserved.\n
           This is not Free or Open Source software.\n
           Please contact Bull SAS for details about its license.\n
           Bull - Rue Jean Jaurès - B.P. 68 - 78340 Les Clayes-sous-Bois

@brief Provides pylinalg qpu
@namespace qat.pylinalg.qpu
@file qat/pylinalg/qpu.py

"""
import qat.pylinalg
import qat.core.qpu as _qpu
import qat.core.qpu.agent as agent
import qat.core.qpu.stateanalyzer as stateanalyzer
_HANDLERS = {
    'agent': agent.GenericAgent,
    'state_analyzer': stateanalyzer.StateAnalyzer,
}
_CLIENT = qat.pylinalg.PyLinalg()
QPU = _qpu.Server(_CLIENT, handlers=_HANDLERS)
