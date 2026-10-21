"""Compare three search methods for a simple coating process model."""
import argparse
import csv
from pathlib import Path
import time
import numpy as np
from scipy.optimize import minimize
import config as cfg
from materials import available_materials, get_material_name, get_material
from process_model import calculate_thickness, calculate_time, calculate_energy


def evaluate_solution(target, length, width, mass_flow, speed, passes, material):
    thickness = calculate_thickness(mass_flow, speed, passes, material, width)
    process_time = calculate_time(speed, length, passes)
    energy = calculate_energy(process_time, cfg.MACHINE_POWER_KW)
    # Squared, uncapped error avoids the flat error plateau in the original score.
    error_term = ((thickness - target) / cfg.THICKNESS_ERROR_SCALE_MM) ** 2
    t_min = calculate_time(cfg.MAX_SPEED, length, min(cfg.PASSES))
    t_max = calculate_time(cfg.MIN_SPEED, length, max(cfg.PASSES))
    time_term = (process_time - t_min) / (t_max - t_min)
    e_min = calculate_energy(t_min, cfg.MACHINE_POWER_KW)
    e_max = calculate_energy(t_max, cfg.MACHINE_POWER_KW)
    energy_term = (energy - e_min) / (e_max - e_min)
    # At constant power, the two normalized terms are mathematically identical.
    score = (cfg.WEIGHT_THICKNESS * error_term + cfg.WEIGHT_TIME * time_term
             + cfg.WEIGHT_ENERGY * energy_term)
    return float(score), float(thickness), float(process_time), float(energy)


def search_grid(target, length, width, material, flows, speeds, initial=None):
    best = initial
    for mass_flow in flows:
        for speed in speeds:
            for passes in cfg.PASSES:
                values = evaluate_solution(target, length, width, mass_flow, speed, passes, material)
                if best is None or values[0] < best['score']:
                    best = {'mass_flow_g_s': float(mass_flow), 'speed_mm_s': float(speed),
                            'passes': passes, 'score': values[0], 'thickness_mm': values[1],
                            'time_s': values[2], 'energy_kwh': values[3]}
    return dict(best)


def fine_grid_bounds(solution):
    return ((max(cfg.MIN_MASS_FLOW, solution['mass_flow_g_s'] - cfg.FINE_MASS_FLOW_MARGIN),
             min(cfg.MAX_MASS_FLOW, solution['mass_flow_g_s'] + cfg.FINE_MASS_FLOW_MARGIN)),
            (max(cfg.MIN_SPEED, solution['speed_mm_s'] - cfg.FINE_SPEED_MARGIN),
             min(cfg.MAX_SPEED, solution['speed_mm_s'] + cfg.FINE_SPEED_MARGIN)))


def local_optimizer(target, length, width, material, seed):
    best = dict(seed)
    failures = []
    x0 = [seed['mass_flow_g_s'], seed['speed_mm_s']]
    for passes in cfg.PASSES:
        def objective(x):
            return evaluate_solution(target, length, width, x[0], x[1], passes, material)[0]
        solution = minimize(objective, x0, method='L-BFGS-B',
                            bounds=[(cfg.MIN_MASS_FLOW, cfg.MAX_MASS_FLOW),
                                    (cfg.MIN_SPEED, cfg.MAX_SPEED)],
                            options={'maxiter': 500, 'ftol': 1e-12, 'gtol': 1e-8})
        if not solution.success or not np.isfinite(solution.fun):
            failures.append(f'Passes {passes}: {solution.message}')
            continue
        values = evaluate_solution(target, length, width, *solution.x, passes, material)
        if values[0] < best['score']:
            best = {'mass_flow_g_s': float(solution.x[0]), 'speed_mm_s': float(solution.x[1]),
                    'passes': passes, 'score': values[0], 'thickness_mm': values[1],
                    'time_s': values[2], 'energy_kwh': values[3]}
    best['status'] = ('Completed' if not failures else
                      f'{len(failures)} run(s) failed; best successful result or coarse seed retained')
    return best, failures


def optimization_general(target, length, width, material_name):
    material = get_material(material_name)
    start = time.perf_counter()
    coarse = search_grid(target, length, width, material, cfg.MASS_FLOW_GRID, cfg.SPEED_GRID)
    coarse['elapsed_s'] = time.perf_counter() - start
    coarse['method'], coarse['status'] = 'Coarse grid', 'Completed'

    start = time.perf_counter()
    flow_bounds, speed_bounds = fine_grid_bounds(coarse)
    # Include the seed exactly, so a sampled refinement cannot lose the coarse result.
    flows = np.unique(np.append(np.linspace(*flow_bounds, cfg.FINE_GRID_POINTS), coarse['mass_flow_g_s']))
    speeds = np.unique(np.append(np.linspace(*speed_bounds, cfg.FINE_GRID_POINTS), coarse['speed_mm_s']))
    fine = search_grid(target, length, width, material, flows, speeds, initial=coarse)
    fine['elapsed_s'] = coarse['elapsed_s'] + time.perf_counter() - start
    fine['method'], fine['status'] = 'Fine grid', 'Completed'

    start = time.perf_counter()
    local, failures = local_optimizer(target, length, width, material, coarse)
    local['elapsed_s'] = coarse['elapsed_s'] + time.perf_counter() - start
    local['method'] = 'Local L-BFGS-B'
    results = [coarse, fine, local]
    for result in results:
        result['error_mm'] = abs(result['thickness_mm'] - target)
        result['within_tolerance'] = result['error_mm'] <= cfg.THICKNESS_TOLERANCE_MM + 1e-12
    return results, failures


def print_results(results, target, length, width, material):
    print(f'\nMaterial: {material} | Target: {target:g} mm | Length: {length:g} mm | Width: {width:g} mm')
    print('\nMethod              Flow[g/s] Speed[mm/s] Passes Thickness[mm] Error[mm] Time[s] Energy[kWh] Score     Elapsed[s]')
    for r in results:
        print(f"{r['method']:<20} {r['mass_flow_g_s']:>8.4f} {r['speed_mm_s']:>10.4f} {r['passes']:>6d} "
              f"{r['thickness_mm']:>12.6f} {r['error_mm']:>9.6f} {r['time_s']:>7.3f} "
              f"{r['energy_kwh']:>11.6f} {r['score']:>9.6f} {r['elapsed_s']:>10.4f}")
        print(f"  Within ±{cfg.THICKNESS_TOLERANCE_MM:g} mm: {r['within_tolerance']} | {r['status']}")
    print('\nElapsed times include the coarse seed for both refinement methods; plotting and input are excluded.')
    print('The score is a trade-off, not a hard thickness constraint. Lower is better.')


def ask_value(message, low, high, integer=False):
    while True:
        try:
            value = int(input(message)) if integer else float(input(message))
            if np.isfinite(value) and low <= value <= high:
                return value
        except ValueError:
            pass
        print(f'Enter a {"whole " if integer else ""}number between {low} and {high}.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--example', action='store_true', help='Run the documented Al2O3 example')
    parser.add_argument('--no-show', action='store_true', help='Save the plot without opening a window')
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'results')
    args = parser.parse_args()
    print('Coating Process Optimizer — simplified deposition model')
    if args.example:
        target, length, width, material_name = 0.5, 1000.0, 10.0, 'Al2O3'
    else:
        target = ask_value('Target thickness [mm]: ', 0.1, 1.0)
        length = ask_value('Coating length [mm]: ', 200, 1500)
        width = ask_value('Effective spray width [mm]: ', 5, 20)
        index = ask_value('Material: 1. Al2O3  2. YSZ  3. NiCr\nSelection: ', 1, 3, integer=True)
        material_name = get_material_name(index)
    mat = get_material(material_name)
    minimum = calculate_thickness(cfg.MIN_MASS_FLOW, cfg.MAX_SPEED, min(cfg.PASSES), mat, width)
    maximum = calculate_thickness(cfg.MAX_MASS_FLOW, cfg.MIN_SPEED, max(cfg.PASSES), mat, width)
    if target < minimum or target > maximum:
        print(f'Note: the exact target is outside the model thickness envelope [{minimum:.4f}, {maximum:.4f}] mm.')
    results, failures = optimization_general(target, length, width, material_name)
    print_results(results, target, length, width, material_name)
    for failure in failures:
        print('Optimizer note:', failure)
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / 'comparison.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    from visualization import plot_comparison
    plot_comparison(results, target, material_name, args.output / 'comparison.png', show=not args.no_show)
    print(f'\nSaved comparison.csv and comparison.png in {args.output}')


if __name__ == '__main__':
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print('\nInput cancelled.')
