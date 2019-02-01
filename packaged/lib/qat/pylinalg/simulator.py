import numpy as np

def output_state_vector(circuit):

    # Initialization at |0...0>
    shape = tuple(2 for _ in range(circuit.nbqbits)) 
    state_vec = np.zeros(shape, dtype=np.complex128)
    state_vec[tuple(0 for _ in range(circuit.nbqbits))] = 1

    # Loop over gates.
    for op in circuit.ops:

        gdef = circuit.gateDic[op.gate]
        matrix = mat2nparray(gdef.matrix) # convert to numpy array.

        tensor = matrix.reshape(tuple(2 for _ in range(2*gdef.arity)))

        #axes for tensor dot: last indices of gate tensor.
        gate_axes = [k for k in range(gdef.arity, 2*gdef.arity, 1)]
        
        # actual gate application
        state_vec = np.tensordot(tensor, state_vec, axes=(gate_axes, op.qbits))

    return state_vec


def mat2nparray(matrix):

    A = np.empty((matrix.nRows, matrix.nCols), dtype=np.complex128) 
           
    cnt = 0
    for i in range(matrix.nRows):
        for j in range(matrix.nCols):
            A[i,j] = matrix.data[cnt].re + 1j*matrix.data[cnt].im
            cnt += 1

    return A    
