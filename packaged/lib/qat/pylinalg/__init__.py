# -*- coding: utf-8 -*-

"""
@authors Bertrand Marchand
@copyright 2019  Bull S.A.S.  -  All rights reserved.\n
           This is not Free or Open Source software.\n
           Please contact Bull SAS for details about its license.\n
           Bull - Rue Jean Jaurès - B.P. 68 - 78340 Les Clayes-sous-Bois
@namespace qat.noisy

"""
from pkgutil import extend_path
import bxi.base.log as logging
import qat.core.qpu as qpu
import qat.core.qpu.agent as agent
import qat.core.qpu.stateanalyzer as stateanalyzer
from .service import PyLinalg


__path__ = extend_path(__path__, __name__)
_LOGGER = logging.getLogger("qat.pylinalg")

_HANDLERS = {
    'agent': agent.GenericAgent,
    'state_analyzer': stateanalyzer.StateAnalyzer,
}

def get_qproc_handler_list():
    """
    Return the list of implemented server
    """
    
    return [PyLinalg]

           Please contact Bull SAS for details about its license.

def get_qpu_server(*args, **kwargs):
"""
    Return a default qpu for noisy qproc

    Returns:
        a qpu handling the simulation within the process

    Note:
        if kwargs contains qpu_handlers they are used as handler of the qpu
    """
    

    qpu_handlers = _HANDLERS
    if "qpu_handlers" in kwargs:
        qpu_handlers.update(kwargs["qpu_handlers"])

    client = PyLinalg(*args, **kwargs)
    return qpu.Server(client, qpu_handlers)

"""
