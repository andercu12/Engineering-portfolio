"""Uniform deposited thickness, travel time and constant-power energy."""
import math


def positive(value, name):
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f'{name} must be finite and positive.')


def check_passes(passes):
    positive(passes, 'Passes')
    if int(passes) != passes:
        raise ValueError('Passes must be an integer.')


def calculate_thickness(mass_flow, speed, passes, mat_data, track_width):
    for value, name in [(mass_flow, 'Mass flow'), (speed, 'Speed'),
                        (track_width, 'Track width'),
                        (mat_data['density_g_cm3'], 'Density')]:
        positive(value, name)
    check_passes(passes)
    efficiency = mat_data['base_efficiency']
    if not math.isfinite(efficiency) or not 0 < efficiency <= 1:
        raise ValueError('Efficiency must be in (0, 1].')
    density_g_mm3 = mat_data['density_g_cm3'] / 1000
    return mass_flow * efficiency * passes / (density_g_mm3 * speed * track_width)


def calculate_time(speed, dist, passes):
    positive(speed, 'Speed')
    positive(dist, 'Coating length')
    check_passes(passes)
    return dist / speed * passes


def calculate_energy(process_time, power):
    positive(process_time, 'Time')
    positive(power, 'Power')
    return power * process_time / 3600
