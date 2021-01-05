from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, execute, Aer
from matplotlib import pyplot as plt
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Operator

import numpy as np
from numpy import sqrt

sim_qasm = Aer.get_backend('qasm_simulator')

U1_op = Operator([[      0.5,        0.5,         0.5,        0.5],
                  [        0,          0, 1 / sqrt(2), -1/sqrt(2)],
                  [1/sqrt(2), -1/sqrt(2),    0,                 0],
                  [      0.5,        0.5, -0.5,              -0.5]])


U1_q = QuantumRegister(2)
U1_c = QuantumCircuit(U1_q, name='U1')
U1_c.unitary(U1_op,[0,1],label = 'label')
U1 = U1_c.to_gate()


def construct_encode(U):
    return U.control(1)


def construct_decode(U):
    # circ = QuantumCircuit(3, name='_decode')
    circ = QuantumCircuit(3, name=U.name + '_decode')
    U_dag = U.inverse()
    circ.x(0)
    circ.append(U_dag.control(1), [0, 1, 2])
    circ.x(0)
    return circ.to_gate()


def construct_alice(U):
    # circ = QuantumCircuit(3, name='Alice_')
    circ = QuantumCircuit(3, name='Alice_' + U.name)
    E = construct_encode(U)
    circ.append(E, [0, 1, 2])
    return circ.to_gate()


def construct_bob(U):
    # circ = QuantumCircuit(3, name='Bob_')
    circ = QuantumCircuit(3, name='Bob_' + U.name)
    D = construct_decode(U)
    circ.append(D, [0, 1, 2])
    return circ.to_gate()

# def no_message_eve(U):

# Entanglement between Alice and Bob
ka = QuantumRegister(1, name='ka')
kb = QuantumRegister(1, name='kb')
# Bit to send
# Bit = 0 -> m[0,1] = |00>
#       1 ->          |01>
m = QuantumRegister(2, name='m')
# Measurement bits for Bob
c = ClassicalRegister(2)

qc = QuantumCircuit(ka, kb, m, c)

# Build EPR pair
qc.h(ka)
qc.cnot(ka, kb)
qc.x(kb)
qc.z(kb)
qc.barrier(ka, kb)

alice = construct_alice(U1)
bob = construct_bob(U1)

# Prepare message: negate iff bit=1
qc.x(m[1])

# Alice encodes the message
qc.append(alice, [ka, m[0], m[1]])

# Bob decodes the message
qc.append(bob, [kb, m[0], m[1]])
# Bob measures the message
qc.measure(m, c)

qc.draw(output='mpl')

job = execute(qc, backend=sim_qasm, shots=1024)
result = job.result()
counts = result.get_counts()
plot_histogram(counts)


# qc_test = QuantumCircuit(2,2)
# qc_test.append(U1,[0,1])
# qc_test.append(U1_dag,[0,1])
# qc_test.measure([0,1],[0,1])
# qc_test.draw(output='mpl')

# job = execute(qc_test, backend=sim_qasm, shots=1024)
# result = job.result()
# counts = result.get_counts()
# plot_histogram(counts)
plt.show()
