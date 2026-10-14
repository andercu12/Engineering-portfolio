# src/process.py

# 
#  --------------------     PROCESS     --------------------
#

def calculate_thickness (mass_flow, speed, passes, mat_data, track_width):

    efficiency = mat_data["base_efficiency"]
    density = mat_data["density_g_cm3"] / 1000
    deposited_mass = mass_flow * efficiency


    #                   mass_fed * deposition_efficiency * number of Passes
    #   thickness = -----------------------------------------------------------------       
    #                       coating density * speed * track width
    
    thickness_per_pass = deposited_mass / (density * speed * track_width)

    total_thickness = thickness_per_pass * passes

    return total_thickness

def calculate_time (speed, dist, passes):

    return (dist/speed) * passes 
    
def calculate_energy (time, power):

    time_h = time / 3600

    return power * time_h
