import time
import numpy as np
from scipy.optimize import minimize, differential_evolution
from tabulate import tabulate
from materials import get_material_name, get_material #Loads material data
from process_model import calculate_thickness, calculate_time, calculate_energy #Loads processes


# ----- PROCESS CHARACTERISTICS ----

# FEED RATE
min_speed = 30 # mm/s
max_speed = 60 # mm/s
SPEED = [30, 40, 50, 60] # mm/s
# MASS FLOW
min_m_flow = 0.5 # g/s
max_m_flow = 2 # g/s
M_FLOW = [0.5, 1, 1.25, 1.5, 2] # g/s
# PASSES
PASSES = [1, 2, 3, 4, 5, 6]
# Machine Power
P = 2.5 # kW 

# 
#  --------------------     OPTIMIZATION ALGORITHMS     --------------------
#
# 0.
def optimization_general (aimed_thickness, longitude, spray_width, mat_name, mat_data):

    # 0. GRID SEARCH: First explore a reference solution
    grid_solution, grid_score, grid_result, GridSearch_duration = optimization_algorithm_GridSearch (aimed_thickness, longitude, spray_width, mat_data )
    print_solutions("Coarse Grid",aimed_thickness, mat_name, grid_solution, grid_score, grid_result)
    # 1. FINE GRID: Parameter space refinemen
    fine_solution, fine_score, fine_result, fine_grid_duration = complemented_optimization (aimed_thickness, longitude, spray_width, mat_data, grid_solution)
    print_solutions("Fine Grid",aimed_thickness, mat_name, fine_solution, fine_score, fine_result)
    fine_grid_total_duration = GridSearch_duration + fine_grid_duration
    # 2. LOCAL OPTIMIZATION: Fine-tuning around good solution 
    local_solution, local_score, local_results, LocalOptimization_duration = local_optimization (aimed_thickness, longitude, spray_width, mat_data, grid_solution)
    print_solutions("Local Optimization L-BFGS-B",aimed_thickness, mat_name, local_solution, local_score, local_results)

    # 3. Benchmark
    headers = ["Method" , "Mass flow", "Speed", "Passes", "Score", "CPU time"]

    data = [["Coarse Grid", grid_solution[0],grid_solution[1], grid_solution[2], grid_score, GridSearch_duration],
            ["Fine Grid", fine_solution[0], fine_solution[1], fine_solution[2], fine_score, fine_grid_total_duration],
            ["Local Optimization", local_solution[0], local_solution[1], local_solution[2], local_score, LocalOptimization_duration]]
    
    print(tabulate(data, headers=headers, tablefmt="github"))

# 0.1
def optimization_algorithm_GridSearch (aimed_thickness, longitude, spray_width, mat_data):

    start_time = time.time()
    best_score = float('inf') 
    best_solution = None
    results = None

    for mass_f in M_FLOW:
        for speed in SPEED:
            for passes in PASSES:
                    
                    score, thickness, process_time, energy = evaluate_solution (aimed_thickness, longitude, spray_width, mass_f, speed, passes, mat_data)

                    if score < best_score:
                        best_solution = [mass_f, speed, passes]
                        results = [thickness, process_time, energy]
                        best_score = score

    end_time = time.time()
    GridSearch_duration = end_time-start_time

    return best_solution, best_score, results, GridSearch_duration
# 1.
def complemented_optimization (aimed_thickness, longitude, spray_width, mat_data, grid_solution):

    # FINE GRID: Parameter space refinement
    # Define newer bounds following the previous solution
    start_time = time.time()
    fine_speed_bounds, fine_m_flow_bounds = fine_grid_bounds (grid_solution)
    best_solution_fine, best_score_fine, result_fine= optimization_algorithm_fine_grid (aimed_thickness, longitude, spray_width, mat_data, fine_speed_bounds, fine_m_flow_bounds)

    end_time = time.time()
    FineGrid_duration = end_time-start_time

    return best_solution_fine, best_score_fine, result_fine, FineGrid_duration
# 1.1
def optimization_algorithm_fine_grid (aimed_thickness, longitude, spray_width,mat_data, fine_speed_bounds, fine_m_flow_bounds):

    best_score = float('inf') 
    best_solution = None
    results = None
    
    v_speed = vectorize_variable (fine_speed_bounds[0], fine_speed_bounds [1])
    v_mass_flow = vectorize_variable (fine_m_flow_bounds [0], fine_m_flow_bounds [1])

    for mass_f in v_mass_flow:
            for speed in v_speed:
                for passes in PASSES:

                    score, thickness, process_time, energy = evaluate_solution (aimed_thickness,longitude,spray_width, mass_f, speed, passes, mat_data)
                    
                    if score < best_score:
                        best_solution = [mass_f, speed, passes]
                        results = [thickness, process_time, energy]
                        best_score = score                    
                                        
    return best_solution,best_score,results
# 1.1.1
def vectorize_variable (lower_limit, higher_limit, n_points = 100):
    return np.linspace (lower_limit, higher_limit, n_points)
# 1.1.2
def fine_grid_bounds (grid_solution):

    mass_min = max(min_m_flow, grid_solution[0] - 0.3)
    mass_max = min(max_m_flow, grid_solution[0] + 0.3)

    speed_min = max(min_speed, grid_solution[1] - 5)
    speed_max = min(max_speed, grid_solution[1] + 5)

    fine_speed_bounds = [speed_min,speed_max]
    fine_m_flow_bounds = [mass_min, mass_max]

    return fine_speed_bounds, fine_m_flow_bounds
# 2.
def local_optimization (aimed_thickness, longitude, spray_width, mat_data, grid_solution):

    start_time = time.time()
    # MATHEMATICAL REFINEMENT: Fine-tuning around good solution
    x0 = [grid_solution[0], grid_solution[1]]
    local_solution, local_score, local_results = local_optimizer (x0, aimed_thickness, longitude, spray_width, mat_data)

    end_time = time.time()
    LocalOptimization_duration = end_time-start_time

    return local_solution, local_score, local_results, LocalOptimization_duration 
# 2.1
def local_optimizer (x0, aimed_thickness, dist, track_width, mat_data):

    # Mass flow, speed, passes
    bounds = [(min_m_flow, max_m_flow), (min_speed, max_speed)]

    best_score = float("inf")

    for passes in PASSES:
        
        # Distance, track width, power, material data
        fixed_args = (aimed_thickness, dist, track_width, mat_data, passes)
        
        solution = minimize (score_eqn, x0, args = fixed_args, method='L-BFGS-B', bounds=bounds)
        

        if solution.fun < best_score:
            best_score = solution.fun
            best_solution = [ solution.x[0], solution.x[1], passes]

            _, thickness, process_time, energy = evaluate_solution (aimed_thickness, dist, track_width, solution.x[0], solution.x[1], passes, mat_data )
            
            best_results = [thickness, process_time, energy]
    
    return best_solution, best_score, best_results
# 2.2
def score_eqn (x, aimed_thickness, dist, track_width, mat_data, pss):

    m_flow = x[0]
    spd= x[1]
    
    # The equation to optimize is the following:
    # w1 * thickness (m_flow, spd, pss) + w2 * time (spd, pss) + w3 * energy (spd, pss)
    # -----------  T1  ---------------- | --------  T2  ------ | -------- T3 ----------
    
    score, _, _, _ = evaluate_solution(aimed_thickness, dist, track_width, m_flow, spd, pss, mat_data)

    return score

# 3.

# def differential_evolution 

#
#  ----------- PRINT SOLUTIONS -------------
#

def print_solutions (message, aimed_thickness, mat_name, best_solution, best_score, result):
 
    print(f"--- RESULTS from {message} ---")
    print("The best found solution is :")

    print(f"\nMaterial: {mat_name}")
    print(f"Mass flow: {best_solution[0]} g/s")
    print(f"Speed: {best_solution[1]} mm/s")
    print(f"Passes: {best_solution[2]}")

    print(f"\nTarget thickness: {aimed_thickness} mm")
    print(f"Predicted thickness : {result[0]} mm")
    error = abs(aimed_thickness-result[0])
    print(f"Error: {error} mm")

    print(f"\nCycle time : {result[1]} s")
    print(f"Energy : {result[2]:.2f} kWh")

    print(f"\nFinal score : {best_score}")

#
#  ----------- SCORE ----------
#

def evaluate_solution (aimed_thickness, longitude, spray_width , m_point, speed, passes, mat_data):

    # Thickness
    max_allowed_error = 0.10
    thickness = calculate_thickness (m_point, speed, passes, mat_data, spray_width)
    error = abs (aimed_thickness - thickness)
    error_norm = min (error / max_allowed_error, 1)

    # Process duration
    process_time = calculate_time (speed, longitude, passes)

    # Energy spent
    energy = calculate_energy (process_time, P)

    w1 = 0.6
    w2 = 0.3
    w3 = 0.1

    time_norm = value_normalization (process_time, min_val = 20 , max_val = 120)
    energy_norm = value_normalization (energy, min_val = 0.2 , max_val = 2)

    score = w1 * error_norm + w2 * time_norm + w3 * energy_norm

    return score, thickness, process_time, energy

#
#  ----------- NORMALIZE VARIABLES ----------
#

def value_normalization (value, min_val, max_val):

    norm_value = (value - min_val) / (max_val - min_val)

    return max(0, min(norm_value, 1))

#
#  ----------- VERIFY INPUT ----------
#

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

# =====================================================================================================
#  MAIN 
# =====================================================================================================

if __name__ == "__main__":

    # Register starting time
    start = time.time()


    print("\n--- Wellcome ---")
    print("The following algorithm optimizes a fictional scenario of a Powder Coating Process.\n")

    aimed_thickness = ask_value_float ("Write the desired thickness [mm]: ", min_val = 0.1, max_val = 1)
    work_longitude = ask_value_float ("Total coating length [mm]: ", min_val = 200, max_val = 1500)
    spray_width = ask_value_float ("Effective spray width [mm]: ", min_val = 5, max_val = 20)
    mat_idx = ask_value_int ("Select coating material:\n1. Al2O3\n2. YSZ\n3. NiCr\nSelection:", min_val = 1, max_val = 3)
    mat_name = get_material_name[mat_idx-1]
    mat_data = get_material[mat_name]

    print("\n--- Input Data Summary ---")
    print(f"Thickness: {aimed_thickness} mm | Coating length: {work_longitude} mm | Spray width: {spray_width} mm | Coating Material: {mat_name} mm \n")
        
    optimization_general (aimed_thickness, work_longitude, spray_width, mat_name, mat_data)

    # Register ending time
    fin = time.time()
    
    # Calculate duration
    duration = fin - start
    minutes = duration // 60
    seconds = duration % 60
    print(f"The operation lasted {minutes:.0f} minutes and {seconds:.0f} seconds.")