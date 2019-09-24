import qiskit
from qiskit.tools.visualization import plot_histogram
import numpy as np

from POVM_functions import nCU1

if __name__ == "__main__":
    # test implementation of a X gate controlled bt three qubits
    q = qiskit.QuantumRegister(4, 'q')
    qc = qiskit.QuantumCircuit(q)

    qc.h(q[0])
    qc.h(q[1])
    qc.h(q[2])

    nCU1('y', np.pi, qc, [q[0]], q[3])

    # Add Measurements

    # Create a Classical Register with 4 bits.
    c = qiskit.ClassicalRegister(4, 'c')
    # Create a Quantum Circuit
    meas = qiskit.QuantumCircuit(q, c)
    meas.barrier(q)
    # map the quantum measurement to the classical bits
    meas.measure(q, c)

    # The Qiskit circuit object supports composition using
    # the addition operator.
    qc = qc + meas

    # Run the quantum circuit on a simulator backend
    backend = qiskit.Aer.get_backend('qasm_simulator')
    shots = 8096

    # Create a Quantum Program for execution
    job = qiskit.execute(qc, backend, shots=shots)

    # execute
    result = job.result()

    counts = result.get_counts(qc)

    plot_histogram(counts)

