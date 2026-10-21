"""Regression checks for mechanics, input validation and report indexing."""
import contextlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import patch
import matplotlib
matplotlib.use('Agg')
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('solver', ROOT / 'src/main.py')
solver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(solver)


def run_case(loads, nodes=None, supports=None, elements=None, plot=None):
    nodes = nodes or ['(0,0)', '(1000,0)', '(0,1000)']
    supports = supports or ['(0,0)', '(1000,0)']
    elements = elements or ['(1,2)', '(1,3)', '(2,3)']
    entries = nodes + ['stop'] + supports + elements + loads
    output = io.StringIO()
    with patch('builtins.input', side_effect=entries), contextlib.redirect_stdout(output):
        result = solver.main(show_plot=False, plot_path=plot)
    return result, output.getvalue()


class SolverTests(unittest.TestCase):
    def test_vertical_both_signs(self):
        for sign in [1, -1]:
            r, _ = run_case(['(0,0)', '(0,0)', f'(0,{sign*1000})'])
            np.testing.assert_allclose(r['displacements'], np.array([0,0,0,0,1/240,1/240])*sign, atol=1e-10)
            np.testing.assert_allclose(r['reactions'], np.array([0,-1000,0,0,0,0])*sign, atol=1e-8)
            np.testing.assert_allclose([e['axial_stress'] for e in r['elements']], [0,sign*5/6,0], atol=1e-10)
            np.testing.assert_allclose(np.asarray(r['node_rows'],dtype=object)[:,2:].astype(float), r['displacements'].reshape(-1,2))

    def test_horizontal_load_explains_report(self):
        r, _ = run_case(['(0,0)', '(0,0)', '(1000,0)'])
        np.testing.assert_allclose(r['reactions'],[-1000,-1000,0,1000,0,0],atol=1e-8)
        np.testing.assert_allclose([e['axial_stress'] for e in r['elements']],[5/6,5/6,-np.sqrt(2)*5/6],atol=1e-10)
        self.assertAlmostEqual(r['reaction_rows'][1][3],1000)
        self.assertAlmostEqual(r['displacements'][4],0.0201184463531091)

    def test_reordered_nodes(self):
        r, _ = run_case(['(0,1000)','(0,0)','(0,0)'],nodes=['(0,1000)','(0,0)','(1000,0)'],elements=['(2,3)','(2,1)','(3,1)'])
        np.testing.assert_allclose(r['displacements'],[1/240,1/240,0,0,0,0],atol=1e-10)
        self.assertAlmostEqual(r['reaction_rows'][0][3],-1000)

    def test_four_nodes(self):
        r, _ = run_case(['(0,0)','(0,0)','(0,-1000)','(0,0)'],nodes=['(0,0)','(1000,0)','(1000,1000)','(0,1000)'],elements=['(1,2)','(2,3)','(3,4)','(4,1)','(1,3)'])
        np.testing.assert_allclose(r['reactions'],[0,0,0,1000,0,0,0,0],atol=1e-8)
        self.assertAlmostEqual(r['reaction_rows'][1][3],1000)

    def test_load_on_support(self):
        r, _ = run_case(['(200,300)','(0,0)','(0,0)'])
        np.testing.assert_allclose(r['displacements'],0,atol=1e-10)
        np.testing.assert_allclose(r['reactions'],[-200,-300,0,0,0,0],atol=1e-8)

    def test_invalid_connections_retry(self):
        r, _ = run_case(['(0,0)','(0,0)','(0,1000)'],elements=['(1,1)','(1,4)','(1,2)','(2,1)','(1, 3)','(2,3)'])
        self.assertEqual(len(r['elements']),3)

    def test_collinear_unstable(self):
        with self.assertRaises(ValueError):
            run_case(['(0,0)']*3,nodes=['(0,0)','(1000,0)','(2000,0)'])

    def test_too_few_nodes(self):
        with patch('builtins.input',side_effect=['(0,0)','stop']), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(ValueError):
                solver.main(show_plot=False)

if __name__ == '__main__':
    unittest.main()
