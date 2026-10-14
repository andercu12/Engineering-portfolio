# src/model.py

import sympy as sp


def build_four_bar_model():

    # Build the symbolic kinematic model of a planar four-bar linkage.
    
    # Define symbolic variables
    # Link length
    l1, l2, l3, l4 = sp.symbols("l1 l2 l3 l4",positive=True)
    
    # Angular coordinates
    theta12, theta23, theta14 = sp.symbols( "theta12 theta23 theta14", real=True)
    
    # Angular velocities
    omega12, omega23, omega14 = sp.symbols("omega12 omega23 omega14",real=True)
    z_dot = sp.Matrix([omega12, omega23,omega14])
    z = sp.Matrix([theta12,theta23,theta14])

    # LOOP EQUATIONS
    # AB + BC = AC (loop 1)
    # AD + DC = AC (loop 2)
    
    # i
    F1 = (l2 * sp.cos(theta12) + l3 * sp.cos(theta23) - l4 * sp.cos(theta14) - l1)

    # j
    F2 = (l2 * sp.sin(theta12) + l3 * sp.sin(theta23) - l4 * sp.sin(theta14))
    
    # Position formulation:
    # F (z) = 0
    # where z = {theta_12, theta_23, theta_14}
    F = sp.Matrix([F1, F2])

    
    # Jacobian
    J = F.jacobian(z)

    # Time derivative of Jacobian
    # J_dot = dJ/dtheta12 * omega12 + dJ/dtheta23 * omega23 + dJ/dtheta14 * omega14
    # J_dot = sum [(i=1) to 4] dJ/dtheta_i * omega_i 
    
    J_dot = sp.zeros(J.rows,J.cols)

    for coordinate, velocity in zip(z,z_dot):

        J_dot += (J.diff(coordinate) * velocity)

    return {
        "lengths": (l1, l2, l3, l4),
        "coordinates": (theta12, theta23, theta14),
        "velocities": (omega12, omega23, omega14),
        "F": F,
        "J": J,
        "J_dot": J_dot
    }


def build_numeric_functions(model):
    
    # Convert symbolic SymPy expressions into numerical functions.

    l1, l2, l3, l4 = model["lengths"]
    theta12, theta23, theta14 = model["coordinates"]
    omega12, omega23, omega14 = model["velocities"]
    F = model["F"]
    J = model["J"]
    J_dot = model["J_dot"]

    # Position constraints
    F_func = sp.lambdify((l1, l2, l3, l4, theta12, theta23, theta14),F,"numpy")
 
    # Jacobian
    J_func = sp.lambdify((l1, l2, l3, l4, theta12, theta23, theta14), J, "numpy")

    # Time derivative of Jacobian
    J_dot_func = sp.lambdify((l1, l2, l3, l4, theta12, theta23, theta14, omega12, omega23, omega14), J_dot, "numpy")

    return {
        "F": F_func,
        "J": J_func,
        "J_dot": J_dot_func
    }