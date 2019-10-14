import numpy as np
import pandas as pd
import sys


import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute
from qiskit.tools.visualization import circuit_drawer
from qiskit import Aer
from qiskit import IBMQ
from qiskit.providers.ibmq import least_busy
from qiskit.tools.visualization import plot_histogram

if __name__ == "__main__":

    phi = float(sys.argv[1])
    print(phi)

    # Create the circuit
    q = QuantumRegister(2, 'q')
    qc = QuantumCircuit(q)

    qc.h(q[0])
    qc.h(q[1])
    qc.rz(phi, q[0])
    qc.ch(q[1], q[0])

    # add measurement
    c = ClassicalRegister(2, 'c')
    meas = QuantumCircuit(q, c)
    meas.measure(q, c)
    qc = qc + meas

    IBMQ.load_accounts()

    shots = 8192  # Number of shots to run the program (experiment); maximum is 8192 shots.
    max_credits = 10  # Maximum number of credits to spend on executions.
    n_qubits = 2

    large_enough_devices = IBMQ.backends(name='ibmqx4')

    backend = least_busy(large_enough_devices)
    print("The best backend is " + backend.name())

    job_exp = execute(qc, backend=backend, shots=shots, max_credits=max_credits)
    result = job_exp.result()

    counts = result.get_counts(qc)

    print("Phi = " + str(phi))
    print(counts)
