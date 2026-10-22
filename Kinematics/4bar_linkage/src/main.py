# src/main.py

import numpy as np
import matplotlib.pyplot as plt

from src.model import (build_four_bar_model, build_numeric_functions)

from src.solvers import (solve_position, solve_velocity, solve_acceleration)

from src.validation import (check_grashof, mechanism_can_close)

from src.visualization import ( initialize_dynamic_plot,
    draw_partial_ground,
    draw_input_link,
    draw_complete_mechanism,
    animate_mechanism)

# ============================================================
# INPUT FUNCTIONS
# ============================================================

def ask_value_float (message, min_val, max_val):
    
   while True:
        try:
            value = float(input(message))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Error: The value has to be between {min_val} and {max_val}")
        except ValueError:
            print ("Error: Please, introduce the correct number.")

def ask_value_int (message, min_val, max_val):
    
   while True:
        try:
            value = int(input(message))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Error: The value has to be between {min_val} and {max_val}")
        except ValueError:
            print ("Error: Please, introduce the correct number.")


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n====================================")
    print("FOUR-BAR KINEMATIC SOLVER")
    print("====================================")

    # --------------------------------------------------------
    # Start interactive plot
    # --------------------------------------------------------

    fig, ax, _ = (initialize_dynamic_plot(max_length=1000))

    # --------------------------------------------------------
    # Geometry input
    # --------------------------------------------------------

    l1 = ask_value_int("\nGround link L1 [mm]: ", min_val = 10, max_val = 1000)

    draw_partial_ground(ax,l1)

    l2 = ask_value_int("Input crank L2 [mm]: ", min_val = 10, max_val = 1000)

    theta12_deg = ask_value_float("Input crank angle θ2 [deg]: " , min_val = 0, max_val = 360)

    theta12 = np.radians(theta12_deg)

    draw_input_link(ax, l1, l2, theta12)

    l3 = ask_value_int("Coupler L3 [mm]: ", min_val =  10, max_val = 1000)

    l4 = ask_value_int("Output rocker L4 [mm]: ", min_val = 10, max_val = 1000)

    lengths = (l1, l2, l3, l4)

    # --------------------------------------------------------
    # Geometry validation
    # --------------------------------------------------------

    if not mechanism_can_close(*lengths):

        print("\nERROR: selected links cannot form a closed mechanism.")
        plt.ioff()
        plt.show()

        return

    if check_grashof(*lengths):

        print("\nGrashof condition satisfied.")

    else:

        print("\nGrashof condition NOT satisfied.")
        print("A complete input-crank revolution may not be possible.")

    # --------------------------------------------------------
    # Build symbolic model
    # --------------------------------------------------------

    symbolic_model = (
        build_four_bar_model()
    )

    numeric_model = (
        build_numeric_functions(
            symbolic_model
        )
    )

    F_func = numeric_model["F"]
    J_func = numeric_model["J"]
    J_dot_func = numeric_model["J_dot"]

    # --------------------------------------------------------
    # Solve initial position
    # --------------------------------------------------------

    initial_guess = np.radians([45.0,90.0])

    try:

        theta23, theta14 = (solve_position(lengths, theta12, F_func, initial_guess))

    except RuntimeError:

        print("\nERROR: the mechanism cannot reach the requested initial configuration.")

        plt.ioff()
        plt.show()

        return

    draw_complete_mechanism(ax, lengths, (theta12,theta23,theta14))

    # --------------------------------------------------------
    # Actuator input
    # --------------------------------------------------------

    omega12 = ask_value_float("\nInput angular velocity ω2 [rad/s]: ", min_val = -100, max_val = 100)

    alpha12 = ask_value_float("Input angular acceleration α2 [rad/s²]: ", min_val = -100, max_val = 100)

    # --------------------------------------------------------
    # Initial velocity solution
    # --------------------------------------------------------

    omega23, omega14 = (solve_velocity(lengths,(theta12,theta23,theta14),omega12,J_func))

    # --------------------------------------------------------
    # Initial acceleration solution
    # --------------------------------------------------------

    alpha23, alpha14 = (solve_acceleration( lengths, (theta12, theta23, theta14), (omega12, omega23, omega14), alpha12, J_func, J_dot_func))

    # --------------------------------------------------------
    # Print initial results
    # --------------------------------------------------------

    print("\n--- INITIAL KINEMATIC STATE ---")

    print(f"\nθ12 = {theta12_deg:.3f}°")
	
    print(f"θ23 = {np.degrees(theta23):.3f}°")

    print(f"θ14 = {np.degrees(theta14):.3f}°")

    print(f"\nω12 = {omega12:.4f} rad/s")

    print(f"ω23 = {omega23:.4f} rad/s")

    print(f"ω14 = {omega14:.4f} rad/s")

    print(f"\nα12 = {alpha12:.4f} rad/s²")

    print(f"α23 = {alpha23:.4f} rad/s²")

    print(f"α14 = {alpha14:.4f} rad/s²")

    input("\nPress ENTER to start simulation...")

    # --------------------------------------------------------
    # Animation
    # --------------------------------------------------------

    print("Angle sweep only: playback timing does not represent the specified actuator motion.")
    plt.close(fig)
    animate_mechanism(lengths, theta12, omega12, alpha12, F_func, J_func, J_dot_func, initial_guess=[theta23,theta14])


if __name__ == "__main__":
    try:
        main()
    except np.linalg.LinAlgError as exc:
        print(f"Cannot calculate this kinematic state: {exc}")
        plt.close("all")