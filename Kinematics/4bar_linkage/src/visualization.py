# src/visualization.py

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from src.solvers import (solve_position, solve_velocity, solve_acceleration)


def joint_coordinates(lengths, angles):
    
    # Calculate Cartesian coordinates of all joints.
    

    l1, l2, l3, l4 = lengths
    theta12, theta23, theta14 = angles

    O2 = np.array([0.0, 0.0])

    O4 = np.array([l1, 0.0])

    A = np.array([l2 * np.cos(theta12), l2 * np.sin(theta12)])

    B = np.array([A[0] + l3 * np.cos(theta23), A[1] + l3 * np.sin(theta23)])

    return O2, A, B, O4


def initialize_dynamic_plot(max_length):
    
    #Create interactive figure.
    
    plt.ion()

    fig, ax = plt.subplots(figsize = (8, 6))

    margin = max_length * 1.5

    ax.set_xlim(-margin, margin)

    ax.set_ylim(-margin, margin)

    ax.set_aspect("equal", adjustable = "box")

    ax.grid(True)

    ax.set_xlabel("X [mm]")

    ax.set_ylabel("Y [mm]")

    ax.set_title("Four-Bar Linkage")

    line, = ax.plot([], [], marker="o", linewidth = 2)

    return fig, ax, line


def draw_partial_ground(ax,l1):
    
    # Draw the ground link while the user is entering data
    ax.plot([0, l1], [0, 0], marker="o")

    ax.figure.canvas.draw()
    ax.figure.canvas.flush_events()


def draw_input_link(ax,l1,l2,theta12):
    
    # Add the input crank to the existing plot.
    

    A_x = (l2 * np.cos(theta12))

    A_y = (l2 * np.sin(theta12))

    ax.clear()

    ax.plot([0, l1], [0, 0], marker="o")

    ax.plot([0, A_x], [0, A_y], marker="o")

    margin = (l1 + l2) * 1.2

    ax.set_xlim(-margin, margin)

    ax.set_ylim(-margin, margin)

    ax.set_aspect("equal")

    ax.grid(True)

    ax.set_xlabel("X [mm]")

    ax.set_ylabel("Y [mm]")

    ax.set_title("Four-Bar Linkage - Input Definition")

    ax.figure.canvas.draw()
    ax.figure.canvas.flush_events()


def draw_complete_mechanism(ax, lengths, angles):
    
    # Draw the complete linkage after successful position solution.
    
    O2, A, B, O4 = joint_coordinates(lengths, angles)

    ax.clear()

    ax.plot(
        [O2[0],A[0],B[0],O4[0]],
        [O2[1],A[1],B[1],O4[1]],
        marker="o"
    )

    max_length = sum(lengths)

    ax.set_xlim(-max_length * 0.25,max_length * 0.75)

    ax.set_ylim(-max_length * 0.50,max_length * 0.50)

    ax.set_aspect("equal")

    ax.grid(True)

    ax.set_xlabel("X [mm]")

    ax.set_ylabel("Y [mm]")

    ax.set_title("Four-Bar Linkage - Initial Configuration")

    ax.figure.canvas.draw()
    ax.figure.canvas.flush_events()


def animate_mechanism(lengths, initial_theta12, omega12, alpha12, F_func, J_func, J_dot_func, initial_guess):
    
    #Animate the mechanism over one complete input revolution.

    #Invalid positions are skipped.
    

    theta12_values = np.linspace(initial_theta12, initial_theta12 + 2*np.pi, 360)

    fig, ax = plt.subplots(figsize=(8, 6))

    max_size = sum(lengths)

    ax.set_xlim(
        -max_size * 0.25,
        max_size * 0.75
    )

    ax.set_ylim(-max_size * 0.50, max_size * 0.50)

    ax.set_aspect("equal")

    ax.grid(True)

    ax.set_xlabel("X [mm]")

    ax.set_ylabel("Y [mm]")

    mechanism_line, = ax.plot([], [], marker="o", linewidth=2)

    trajectory_line, = ax.plot([], [], linestyle="--")

    trajectory_x = []
    trajectory_y = []

    current_guess = np.array(initial_guess, dtype=float)

    def update(frame):

        nonlocal current_guess

        theta12 = theta12_values[frame]

        try:

            theta23, theta14 = (solve_position(lengths, theta12, F_func, current_guess))

        except RuntimeError:

            return (mechanism_line, trajectory_line)

        # Previous solution becomes next initial guess.
        current_guess = np.array([theta23, theta14])

        # -------------------------------
        # Velocity
        # -------------------------------

        omega23, omega14 = (solve_velocity(lengths, (theta12, theta23, theta14), omega12, J_func))

        # -------------------------------
        # Acceleration
        # -------------------------------

        alpha23, alpha14 = (solve_acceleration(lengths, (theta12,theta23,theta14), (omega12,omega23,omega14), alpha12, J_func, J_dot_func))

        O2, A, B, O4 = (joint_coordinates(lengths,(theta12,theta23,theta14)))
                

        x_values = [O2[0], A[0], B[0], O4[0]]

        y_values = [O2[1], A[1], B[1], O4[1]]

        mechanism_line.set_data(x_values, y_values)

        # Track output joint B
        trajectory_x.append(B[0])

        trajectory_y.append(B[1])

        trajectory_line.set_data(trajectory_x, trajectory_y)

        ax.set_title(
            "Four-Bar Linkage\n"
            f"θ2 = {np.degrees(theta12):.1f}° | "
            f"ω3 = {omega23:.2f} rad/s | "
            f"ω4 = {omega14:.2f} rad/s | "
            f"α3 = {alpha23:.2f} rad/s² | "
            f"α4 = {alpha14:.2f} rad/s²"
        )

        return (mechanism_line, trajectory_line)

    animation = FuncAnimation(fig, update, frames=len(theta12_values), interval=30, blit=False, repeat=True)

    plt.ioff()
    plt.show()

    return animation