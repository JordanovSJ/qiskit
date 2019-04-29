import numpy as np
import pandas as pd
import sys

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute
from qiskit import Aer
from qiskit import IBMQ
from qiskit.quantum_info import state_fidelity
import datetime


def state_vector(counts):

    terms = list(counts.keys())
    terms.sort()
    last = terms[-1]
    n = len(last)

    vector = np.zeros(2**n)
    vector_module = 0

    for term in terms:
        i = int(term, 2)

        vector[i] = counts[term]
        vector_module += vector[i]*vector[i]

    return vector / np.sqrt(vector_module)


def ghz(n):

    vector = np.zeros(2**n)
    vector[0] = 1 / np.sqrt(2)
    vector[-1] = vector[0]
    return vector


if __name__ == "__main__":

    n = int(sys.argv[1])
    N_wait = int(sys.argv[2])

    print('n_qubits =' + str(n))
    print('N_wait =' + str(N_wait))

    if n > 1:

        experiment = 1

        q = QuantumRegister(n)
        qc = QuantumCircuit(q)

        # operations
        if n == 2:
            qc.h(q[1])
            qc.cx(q[1], q[0])
            # qc.cx(q[2], q[1])

        if n == 3:
            qc.h(q[2])
            qc.cx(q[2], q[1])
            qc.cx(q[1], q[0])

        if n == 4:
            qc.h(q[3])
            qc.cx(q[3], q[2])
            qc.cx(q[2], q[1])
            qc.cx(q[1], q[0])

        if n == 5:
            qc.h(q[3])
            qc.cx(q[3], q[4])
            qc.cx(q[3], q[2])
            qc.cx(q[2], q[1])
            qc.cx(q[1], q[0])

        #WAIT
        for i in range(N_wait):
            for qj in q:
                qc.iden(qj)

        # measurement
        c = ClassicalRegister(n, 'c')
        meas = QuantumCircuit(q, c)
        meas.measure(q, c)
        qc = qc + meas

        if experiment != 1:
            # Run the quantum circuit on a simulator backend
            backend = Aer.get_backend('qasm_simulator')
            shots = 8096
            job = execute(qc, backend, shots=shots)
            result = job.result()
        elif experiment == 1:
            IBMQ.load_accounts()

            shots = 8192  # Number of shots to run the program (experiment); maximum is 8192 shots.
            max_credits = 10  # Maximum number of credits to spend on executions.
            n_qubits = n

            backend = IBMQ.backends(name='ibmqx4')[0]

            print("The best backend is " + backend.name())
            job_exp = execute(qc, backend=backend, shots=shots, max_credits=max_credits)
            result = job_exp.result()

        counts = result.get_counts(qc)

        desired_vector = ghz(n)
        qc_state = state_vector(counts)
        x = state_fidelity(desired_vector, qc_state)
        print(counts)

        print(desired_vector)
        print(qc_state)
        print(x)
        print(datetime.datetime.now())

    else:
        print('Wrong parameter input!')