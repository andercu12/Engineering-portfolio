"""Small checks for units, normalization and the search methods."""
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import config as cfg
from materials import get_material, get_material_name
from process_model import calculate_thickness, calculate_time, calculate_energy
from main import evaluate_solution, optimization_general


class ModelTests(unittest.TestCase):
    def test_material_lookup(self):
        self.assertEqual(get_material_name(1), 'Al2O3')
        self.assertEqual(get_material('NiCr')['density_g_cm3'], 8.2)

    def test_units_and_mass_balance(self):
        mat = get_material('Al2O3')
        thickness = calculate_thickness(1, 50, 2, mat, 10)
        self.assertAlmostEqual(thickness, 0.5569620253164557)
        duration = calculate_time(50, 1000, 2)
        self.assertEqual(duration, 40)
        self.assertAlmostEqual(calculate_energy(duration, 2.5), 0.0277777777777778)
        self.assertAlmostEqual(thickness * 1000 * 10 * 0.00395, 1 * duration * 0.55)

    def test_length_scaling(self):
        mat = get_material('Al2O3')
        a = evaluate_solution(0.5, 500, 10, 1, 50, 2, mat)
        b = evaluate_solution(0.5, 1000, 10, 1, 50, 2, mat)
        self.assertAlmostEqual(a[0], b[0])
        self.assertEqual(a[1], b[1])
        self.assertEqual(2*a[2], b[2])
        self.assertEqual(2*a[3], b[3])

    def test_invalid_physics(self):
        for speed in [0, -1, float('nan')]:
            with self.assertRaises(ValueError):
                calculate_time(speed, 1000, 1)
        with self.assertRaises(ValueError):
            calculate_time(50, 1000, 1.5)

    def test_searches_and_local_reference(self):
        results, failures = optimization_general(0.5, 1000, 10, 'Al2O3')
        self.assertFalse(failures)
        self.assertLessEqual(results[1]['score'], results[0]['score'] + 1e-12)
        self.assertLessEqual(results[2]['score'], results[0]['score'] + 1e-12)
        # Independent reduction: at each speed/pass count, the best flow is the
        # exact-thickness flow clipped to bounds (time does not depend on flow).
        speeds = np.linspace(30, 60, 100001)
        best = float('inf')
        for passes in cfg.PASSES:
            flow = np.clip(0.5 * 0.00395 * speeds * 10 / (0.55 * passes), 0.5, 2)
            h = flow * 0.55 * passes / (0.00395 * speeds * 10)
            t = 1000 / speeds * passes
            score = 0.6*((h-0.5)/0.1)**2 + 0.4*(t-1000/60)/(200-1000/60)
            best = min(best, float(score.min()))
        self.assertAlmostEqual(results[2]['score'], best, delta=1e-7)
        for r in results:
            self.assertIn(r['passes'], cfg.PASSES)
            self.assertTrue(0.5 <= r['mass_flow_g_s'] <= 2)
            self.assertTrue(30 <= r['speed_mm_s'] <= 60)

if __name__ == '__main__':
    unittest.main()
