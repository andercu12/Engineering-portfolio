# src/solvers.py

import numpy as np
from scipy.optimize import root


def solve_position(lengths, theta12, F_func, initial_guess):
    
    # Solve theta23 and theta14 for a known theta12.

    l1, l2, l3, l4 = lengths

    def residual(unknown_angles):

        theta23 = unknown_angles[0]
        theta14 = unknown_angles[1]

        values = F_func(l1, l2, l3, l4, theta12, theta23, theta14)

        return np.asarray(values, dtype=float).flatten()

    solution = root(residual, initial_guess)

    if (not solution.success or not np.all(np.isfinite(solution.x))
            or np.linalg.norm(residual(solution.x), ord=np.inf) > 1e-8 * max(lengths)):

        raise RuntimeError("Position solver failed to converge.")

    theta23 = solution.x[0]
    theta14 = solution.x[1]

    return theta23, theta14


def solve_velocity(lengths,angles, omega12 ,J_func):
    
    #Solve angular velocities omega3 and omega4.
    #Uses: J * z_dot = 0

    l1, l2, l3, l4 = lengths
    theta12, theta23, theta14 = angles

    J = np.asarray(J_func(l1 ,l2, l3, l4, theta12, theta23, theta14), dtype=float)

    # First column -> prescribed coordinate theta2
    J_input = J[:, 0]

    # Remaining columns -> unknown coordinates
    J_unknown = J[:, 1:]

    if np.linalg.cond(J_unknown) > 1e12:
        raise np.linalg.LinAlgError("Singular or near-singular linkage configuration.")

    rhs = (-J_input * omega12)

    omega23, omega14 = np.linalg.solve(J_unknown,rhs)

    return omega23, omega14


def solve_acceleration(lengths, angles, angular_velocities, alpha12, J_func, J_dot_func):
   
    #Solve angular accelerations alpha3 and alpha4.
    #Uses: J * z_ddot + J_dot * z_dot = 0
    
    l1, l2, l3, l4 = lengths

    theta12, theta23, theta14 = angles

    omega12, omega23, omega14 = (angular_velocities)

    
    # Evaluate Jacobian
    
    J = np.asarray(J_func(l1, l2, l3, l4, theta12, theta23, theta14), dtype=float)

    
    # Evaluate time derivative of Jacobian
    
    J_dot = np.asarray(J_dot_func(l1, l2, l3, l4, theta12, theta23, theta14, omega12, omega23, omega14), dtype=float)

    z_dot = np.array([omega12,omega23,omega14])

    J_input = J[:, 0]
    J_unknown = J[:, 1:]

    if np.linalg.cond(J_unknown) > 1e12:
        raise np.linalg.LinAlgError("Singular or near-singular linkage configuration.")

    dynamic_term = (J_dot @ z_dot)

    # J_unknown * [alpha23, alpha14]
    # =
    # -J_input * alpha12
    # -J_dot * z_dot

    rhs = (-J_input * alpha12 - dynamic_term)

    alpha23, alpha14 = np.linalg.solve(J_unknown,rhs)

    return alpha23, alpha14