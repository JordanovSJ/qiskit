import qiskit
# from qiskit.tools.visualization import plot_histogram
import numpy as np


# works
def toffoli_gate(q_circ, ctrl_q1, ctrl_q2, target_q):

    q_circ.cu3(np.pi/2, 0, 0, ctrl_q2, target_q)
    q_circ.cx(ctrl_q1, target_q)
    q_circ.cu3(-np.pi / 2, 0, 0, ctrl_q2, target_q)
    q_circ.cx(ctrl_q1, target_q)


def CCCNot(q_circ, ctrl1, ctrl2, ctrl3, target):

    # TODO
    return 0


if __name__ == "__main__":
    q = qiskit.QuantumRegister(3, 'q')
    qc = qiskit.QuantumCircuit(q)

    qc.h(q[0])
    qc.h(q[1])

    toffoli_gate(qc, q[0], q[1], q[2])

    # Add Measurements

    # Create a Classical Register with 3 bits.
    c = qiskit.ClassicalRegister(3, 'c')
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
    print(counts)
    # plot_histogram(counts)

