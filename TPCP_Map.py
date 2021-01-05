#########################################################################################
#                                       import                                          #                        
#########################################################################################
import numpy as np
from qiskit import *
from qiskit.visualization import plot_histogram
from numpy.random import randint
from matplotlib import pyplot as plt
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, execute, BasicAer, IBMQ
from qiskit import QuantumCircuit, execute, Aer
from Alice_Bob import construct_alice, construct_bob, construct_decode, construct_encode

#########################################################################################
#                                    Alice's bit                                        #                        
#########################################################################################
# |phi_i>: 2 qubits
alice_qubits = randint(2, size=2)
bit_mapping = {'00': [1, 0, 0, 0], '01': [0, 1, 0, 0], '10': [0, 0, 1, 0], '11': [0, 0, 0, 1]}
alice_bits = np.matrix(np.reshape(bit_mapping[str(alice_qubits[0])+str(alice_qubits[1])], (4, 1)))
print("alice_bits: \n", alice_bits)

#########################################################################################
#                                     U_episolon                                        #                        
#########################################################################################
M_0 = np.identity(2)
# M_1 = np.zeros([2, 2])
M_1 = np.identity(2)
# M_2 = np.zeros([2, 2])
M_2 = np.identity(2)
M_3 = np.identity(2)
# U_epi is an identity matrix (default)
U_epi = np.matrix(np.vstack((np.hstack((M_0, M_1)), np.hstack((M_2, M_3)))))
U_epi_dagger = np.matrix(U_epi).H.T
print("U_epi: \n", U_epi)
print("U_epi_dagger: \n", U_epi_dagger)

#########################################################################################
#                                        U_E                                            #                        
#########################################################################################
M_0_E = np.identity(2)
M_1_E = np.identity(2)
ZERO_E = np.zeros([2, 2])
# U_E is an identity matrix (default)
U_E = np.matrix(np.vstack((np.hstack((M_0_E, ZERO_E)), np.hstack((ZERO_E, M_1_E)))))
U_E_dagger = np.matrix(U_E).H.T
print("U_E: \n", U_E)
print("U_E_dagger: \n", U_E_dagger)

#########################################################################################
#                                        rho                                            #                        
#########################################################################################
# Alice
rho_i = np.matrix(alice_bits*np.reshape(alice_bits, (1, 4)))
print("rho: \n", rho_i)
# Alice + Bob 
rho_i_prime = 0.5*(rho_i + U_epi*rho_i*U_epi_dagger)
print("rho_i_prime: \n", rho_i_prime)
# Eve mapping "rho_i_prime" --> "rho_E_prime" --> send to Bob to decode --> "rho_E_double_prime" --> measure --> "phi_j"
rho_E_double_prime = 0.5*(U_E*rho_i*U_E_dagger + U_epi_dagger*U_E*U_epi*rho_i*U_epi_dagger*U_E_dagger*U_epi)
print("rho_E_double_prime: \n", rho_E_double_prime)

#########################################################################################
#                                    Eve Achieve                                        #                        
#########################################################################################
# Probability of Eve substituting an authentic message with a different one that passes Bob’s test
# Define |phi_j>: "bob_bits"
P_eve = 0.5*(abs(bob_bits*U_E*alice_bits)**2 + abs(bob_bits*U_epi_dagger*U_E*U_epi*alice_bits)**2)
print("P_f_prime: \n", P_eve)

#########################################################################################
#                                    Alice & Bob                                        #                        
#########################################################################################
sim_qasm = Aer.get_backend('qasm_simulator')

U1_q = QuantumRegister(2)
U1_c = QuantumCircuit(U1_q, name='U1')
U1 = U1_c.to_gate()
U1_dag = U1.inverse()

ka = QuantumRegister(1, name='ka')
kb = QuantumRegister(1, name='kb')
m = QuantumRegister(2, name='m')
c = ClassicalRegister(2)
qc = QuantumCircuit(ka, kb, m, c)

# Build EPR pair
qc.h(ka)
qc.cnot(ka, kb)
qc.x(kb)
qc.z(kb)
qc.barrier(ka,kb)

alice = construct_alice(U1)
bob = construct_bob(U1)

qc.append(alice, [ka, m[0], m[1]])
qc.append(bob, [kb, m[0], m[1]])

# qc.measure(m, c)
# qc.draw(output='mpl')

# job = execute(qc, backend=sim_qasm, shots=1e6)
# result = job.result()
# counts = result.get_counts()
# plot_histogram(counts)

# plt.show()