from numpy import pi
import numpy as np

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute
from qiskit import IBMQ


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


# n-qubit control rotation gate
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

        nCU1(axis, angle / 2, q_circ, new_ctrls, target)
        q_circ.cx(list_ctrls[-1], target)
        nCU1(axis, -angle / 2, q_circ, new_ctrls, target)
        q_circ.cx(list_ctrls[-1], target)
    elif n_ctrls == 1:

        if axis == 'y':
            #             q_circ.cu3(angle, 0, 0, list_ctrls[0], target)
            q_circ.u3(angle / 2, 0, 0, target)
            q_circ.cx(list_ctrls[0], target)
            q_circ.u3(-angle / 2, 0, 0, target)
            q_circ.cx(list_ctrls[0], target)

        elif axis == 'z':
            #             q_circ.cu3(0, 0, angle, list_ctrls[0], target)
            q_circ.u3(0, 0, angle / 2, target)
            q_circ.cx(list_ctrls[0], target)
            q_circ.u3(0, 0, -angle / 2, target)
            q_circ.cx(list_ctrls[0], target)

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
    # TODO: implement a multi-qubit controlled gates, using additional auxiliary qubits and linear complexity
    return 1


def first_AP_module_new(qc, q, tita1, tita2, phi1, phi2):
    """ Implements a first module of Ahenrt Payne POVM.

        qc: existing q-circuit

        q: is a register of at least 3 qubit objects.
        q[0] represents the state being measured
        q[1] is ancilla qubit, used to represent the output branches. It should be in the zero state
        q[2], is another ancilla qubit, required for intermidiate operations. It should be in zero state too

        The outputs (branches) correspond to the following values of q1:
            branch p1: 0
            branch p2: 1

        tita1 and tita2 specify POVMs 1 and 2(see above)
        (future version will allow for phase operations, specified by phi1 and phi2)
    """

    # Split in paths p1 and p2
    qc.cx(q[0], q[1])
    # Apply the rotations along p1 and p2

    # controlled rotation if qubit 1 is ZERO
    qc.x(q[1])
    #     qc.cu3(2*(tita1 + pi/2),0,0,q[1],q[0])
    nCU1('y', 2 * (tita1 + pi / 2), qc, [q[1]], q[0])
    qc.x(q[1])

    # controlled rotation if qubit 1 is ONE
    #     qc.cu3(2*tita2,0,0,q[1],q[0])
    nCU1('y', 2 * tita2, qc, [q[1]], q[0])

    # Now instead of t branching swap the second ancilla qubit
    qc.cx(q[0], q[1])
    qc.cx(q[1], q[0])
    qc.cx(q[0], q[1])

    qc.x(q[1])
    qc.z(q[1])  # u3(0,0,pi,q[1])  # not sure if neccessery for the correct output!!!

    # phase shifts:
    if phi1 != 0 or phi2 != 0:
        qc.x(q[1])
        #     qc.cu3(0,0,phi2,q[1], q[0])
        nCU1('z', phi1, qc, [q[1]], q[0])
        qc.x(q[1])

        #     qc.cu3(0,0,phi2,q[1], q[0])
        nCU1('z', phi2, qc, [q[1]], q[0])


def second_AP_module_new(qc, q, tita3, tita4):
    """ Implements a second module of Ahenrt Payne POVM.

        qc: existing q-circuit

        q: is a register of at least 4 qubit objects.
        q[0] represents the state being measured
        q[1], q[2] are ancilla qubits, used to represent the output branches. They should be in the zero state
        q[3], is another ancilla qubit, required for intermidiate operations. It should be in zero state too

        The outputs (branches) correspond to the following values of q1q2:
            branch p1: 00
            branch p2: 10
            branch p3: 11

        tita3 and tita4 specify POVMs 3 and 4(see above)
        (future version will allow for phase operations, specified by phi2 and phi3)
    """

    # Split in branches p3 and p4
    qc.ccx(q[0], q[1], q[2])

    # Apply the rotations along p1' and p2'

    # Rotation along p1' branch
    qc.x(q[2])
    nCU1('y', 2 * (tita3 + pi / 2), qc, [q[1], q[2]], q[0])
    qc.x(q[2])

    # rotation along p2' branch
    nCU1('y', 2 * tita4, qc, [q[1], q[2]], q[0])

    # instead of t branchin c-swap q0 and q2 if q1
    qc.cswap(q[1], q[0], q[2])
    qc.cx(q[1], q[2])
    qc.cu3(0, 0, pi, q[1], q[2])


def two_part_POVM():
    # Create a Quantum Register with 3 qubits.
    q = QuantumRegister(2, 'q')

    # Create a Quantum Circuit acting on the q register
    qc = QuantumCircuit(q)

    # Add waiting time
    for i in range(1000):
        qc.iden(q)

    # prepare the input state (the input state will be represented by qubit 0)
    qc.u3(pi * 2 / 3, 0, 0, q[0])
    # qc.barrier(q)

    # Apply the POVM
    first_AP_module_new(qc, q, pi / 4, pi / 4, 0, 0)

    # Add Measurements

    # Create a Classical Register with 3 bits.
    c = ClassicalRegister(2, 'c')
    # Create a Quantum Circuit
    meas = QuantumCircuit(q, c)

    # map the quantum measurement to the classical bits
    meas.measure(q, c)

    # The Qiskit circuit object supports composition using
    # the addition operator.
    qc = qc + meas

    # IBMQ.save_account(token)
    IBMQ.load_accounts()

    shots = 8192  # Number of shots to run the program (experiment); maximum is 8192 shots.
    max_credits = 10  # Maximum number of credits to spend on executions.
    n_qubits = 3

    backend = IBMQ.backends(name='ibmqx4')[0]

    print("The best backend is " + backend.name())

    # <<<<<<<<<<< EXECUTING real experiment >>>>>>>>>>>>>>
    run = 1  # keep 0 untill you want to run the experiment, to avoid running by mistake. It is slow and cost credits!
    if run:
        job_exp = execute(qc, backend=backend, shots=shots, max_credits=max_credits)
        result = job_exp.result()

    counts = result.get_counts(qc)

    print(counts)


def three_part_POVM():
    # angle parameters for the 1st and 2nd panel
    tita1 = np.arccos(np.sqrt(2 / 3))
    tita2 = pi / 2
    tita3 = 0
    tita4 = pi / 2

    # Ui and Uii are implemented as controled rotations as well.
    # In our example Ui = I, so no action needed
    # For Uii required y rotation at -pi/2 rads

    alpha_ui = 0
    alpha_uii = -pi / 2

    # Create a Quantum Register with 4 qubits.
    q = QuantumRegister(3, 'q')

    # Create a Quantum Circuit acting on the q register
    qc = QuantumCircuit(q)

    # qc.u3(0, 0, 0, q[0])  # INITIAL STATE!

    # Apply Ui
    # qc.u3(alpha_ui, 0, 0, q[0])  # for the sake of clarity

    # Apply the 1st AnP panel
    first_AP_module_new(qc, q, tita1, tita2, 0, 0)

    # Apply Uii, require a single qubit controled rotation
    nCU1('y', alpha_uii, qc, [q[1]], q[0])

    # Apply 2nd Ahnert Payne POVM module
    second_AP_module_new(qc, q, tita3, tita4)

    # KRAUS OPERATORS
    kraus = 1
    if kraus:
        # perform T2 on p2 branch, correspond to 10 value of q1q2
        qc.x(q[2])
        # nCU1('y', 2*pi/3, qc, [q[1], q[2]], q[0] )
        nCU1('y', 2 * pi / 3, qc, [q[1], q[2]], q[0])
        qc.x(q[2])

        # perform T3 on p3 branch, correspond to 11 value of q1q2
        # nCU1('y', -2*pi/3, qc, [q[1], q[2]], q[0] )  # changee???
        nCU1('y', 7 * pi / 3, qc, [q[1], q[2]], q[0])

        # 11->01
        qc.cx(q[2], q[1])

    # Add Measurements

    # Create a Classical Register with 3 bits.
    c = ClassicalRegister(3, 'c')
    # Create a Quantum Circuit
    meas = QuantumCircuit(q, c)
    meas.barrier(q)
    # map the quantum measurement to the classical bits
    meas.measure(q, c)

    # The Qiskit circuit object supports composition using
    # the addition operator.
    qc = qc + meas

    # IBMQ.save_account(token)
    IBMQ.load_accounts()

    shots = 8192  # Number of shots to run the program (experiment); maximum is 8192 shots.
    max_credits = 10  # Maximum number of credits to spend on executions.
    n_qubits = 3

    backend = IBMQ.backends(name='ibmqx4')[0]
    print("The best backend is " + backend.name())

    # Hello there
    # <<<<<<<<<<< EXECUTING real experiment >>>>>>>>>>>>>>
    run = 1  # keep 0 untill you want to run the experiment, to avoid running by mistake. It is slow and cost credits!
    if run:
        job_exp = execute(qc, backend=backend, shots=shots, max_credits=max_credits)
        result = job_exp.result()

    counts = result.get_counts(qc)
    print(counts)


if __name__ == "__main__":
    # three_part_POVM()
    # two_part_POVM()
    print("PIZZA")
