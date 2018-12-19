import qiskit
from qiskit.tools.visualization import plot_histogram
import numpy as np
# import matplotlib.pyplot as plt


# works
def toffoli_gate(q_circ, ctrl_q1, ctrl_q2, target_q):

    q_circ.cu3(np.pi/2, 0, 0, ctrl_q2, target_q)
    q_circ.cx(ctrl_q1, target_q)
    q_circ.cu3(-np.pi / 2, 0, 0, ctrl_q2, target_q)
    q_circ.cx(ctrl_q1, target_q)


def CCU1(axis, angle, q_circ, ctrl1, ctrl2, target):
    """ Add gates acting as a doubly controlled rotation gate to an existing
        quantum circuit.
        Valid values for axis: 'y' and 'z' (any rotation can be specified by Y and
        Z rotations only, no need for X).
    """
    if axis == 'y':
        q_circ.cu3(angle / 2, 0, 0, ctrl1, target)
        q_circ.cx(ctrl2, target)
        q_circ.cu3(-angle / 2, 0, 0, ctrl1, target)
        q_circ.cx(ctrl2, target)
    elif axis == 'z':
        q_circ.cu3(0, 0, angle / 2, ctrl1, target)
        q_circ.cx(ctrl2, target)
        q_circ.cu3(0, 0, -angle / 2, ctrl1, target)
        q_circ.cx(ctrl2, target)
    else:
        raise ValueError('Rotational axis not valid')


def CCCU1(axis, angle, q_circ, ctrl1, ctrl2, ctrl3, target):
    """ Add gates acting as a triple controlled rotation gate, to an existing
        quantum circuit.
        Valid values for axis: 'y' and 'z' (any rotation can be specified by Y and
        Z rotations only, no need for X).
    """
    CCU1(axis, angle/2, q_circ, ctrl1, ctrl2, target)
    q_circ.cx(ctrl3, target)
    CCU1(axis, -angle / 2, q_circ, ctrl1, ctrl2, target)
    q_circ.cx(ctrl3, target)


def nCU1(axis, angle, q_circ, ctrls, target):
    """
        Implements n-qubit controlled rotation (nCU1 )
        The rotation is single axial (unlike the qiskit multi axial rotation u3),
        Parameters:
        * axis: specifies the rotation, acceptable char values 'y' and 'z'
        (note: y and z rotation can be combined to implement any single qubit
        unitary operation)
        * angle: Bloch sphere angle specifying the rotation
        * q_circ: the quantum circuit to, which the nCU1 operation is added
        * ctrls: a list or quantum register of the control qubits.
        * target: the target qubit
    """

    n_ctrls = len(ctrls)
    list_ctrls = list(ctrls)  # a list of the qubits is easier to work with, than the QuantumRegister object
    new_ctrls = list_ctrls[:-1]  # take all control qubits references but the last one

    if n_ctrls >= 2:

        nCU1(axis, angle/2, q_circ, new_ctrls, target)
        q_circ.cx(list_ctrls[-1], target)
        nCU1(axis, -angle / 2, q_circ, new_ctrls, target)
        q_circ.cx(list_ctrls[-1], target)
    elif n_ctrls == 1:

        if axis == 'y':
            q_circ.cu3(angle, 0, 0, list_ctrls[0], target)
        elif axis == 'z':
            q_circ.cu3(0, 0, angle, list_ctrls[0], target)
        else:
            raise ValueError('Invalid value for axis!')
    else:

        if axis == 'y':
            q_circ.u3(angle, 0, 0, target)
        elif axis == 'z':
            q_circ.u3(0, 0, angle, target)
        else:
            raise ValueError('Invalid value for axis!')

    return 1


def nCU1_ancilla():
    # TODO
    return 1


if __name__ == "__main__":
    q = qiskit.QuantumRegister(4, 'q')
    qc = qiskit.QuantumCircuit(q)

    qc.h(q[0])
    qc.h(q[1])
    qc.h(q[2])

    nCU1('y', np.pi, qc, [q[0]], q[3])

    # Add Measurements

    # Create a Classical Register with 3 bits.
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

