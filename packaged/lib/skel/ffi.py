# -*- coding: utf-8 -*-

"""
@authors Pierre Vignéras <pierre.vigneras@atos.net>
@copyright 2013  Bull S.A.S.  -  All rights reserved.\n
           This is not Free or Open Source software.\n
           Please contact Bull SAS for details about its license.\n
           Bull - Rue Jean Jaurès - B.P. 68 - 78340 Les Clayes-sous-Bois
@namespace skel.ffi Python skel CFFI instance and tools

"""

import cffi
import cffi.api

__FFI__ = cffi.FFI()


# C helper functions
try:
    __FFI__.cdef('''FILE *fmemopen(void *, size_t, const char*);
                 int fclose(FILE*);
                 void free(void *ptr);
                 ''')
except cffi.FFIError:
    # only once is needed
    pass


def add_cdef_for_type(ctype, cdef, packed=False):
    '''
    Define the given cdef, only if given ctype isn't defined yet.

    Warning: this doesn't work for function ctype !

    @return None
    '''
    try:
        __FFI__.getctype(ctype)
    except cffi.api.CDefError:
        __FFI__.cdef(cdef, packed)


def get_ffi():
    """
    Return the ffi object used by this module to interact with the C backend.

    @return the ffi object used by this module to interact with the C backend.
    """
    return __FFI__
