"""Checks for the example and the Jacobian-based derivatives."""
import unittest
import numpy as np
from src.model import build_four_bar_model, build_numeric_functions
from src.solvers import solve_position, solve_velocity, solve_acceleration
from src.validation import check_grashof, mechanism_can_close
from examples.run_example import sample_cycle, LENGTHS


class KinematicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = build_numeric_functions(build_four_bar_model())

    def test_full_cycle_geometry(self):
        rows, points = sample_cycle()
        self.assertLess(rows[:,-1].max(), 1e-6)
        np.testing.assert_allclose(points[0],points[-1],atol=1e-6)
        for i, length in enumerate(LENGTHS[1:]):
            np.testing.assert_allclose(np.linalg.norm(points[:,i+1]-points[:,i],axis=1),length,atol=1e-6)

    def test_derivatives_against_position_differences(self):
        # Include nonzero input acceleration, independently differentiating positions.
        theta = np.radians(65)
        omega, alpha = 1.7, 0.8
        q = solve_position(LENGTHS,theta,self.f['F'],np.radians([45,90]))
        v = solve_velocity(LENGTHS,(theta,*q),omega,self.f['J'])
        a = solve_acceleration(LENGTHS,(theta,*q),(omega,*v),alpha,self.f['J'],self.f['J_dot'])
        dt = 1e-3
        def position(t):
            return np.array(solve_position(LENGTHS,theta+omega*t+0.5*alpha*t*t,self.f['F'],q))
        before, middle, after = position(-dt),np.array(q),position(dt)
        np.testing.assert_allclose(v,(after-before)/(2*dt),atol=5e-6,rtol=1e-5)
        np.testing.assert_allclose(a,(after-2*middle+before)/dt**2,atol=3e-5,rtol=1e-4)

    def test_unreachable_angle(self):
        # These lengths close at some angles, but not at theta2 = pi.
        lengths=(150,100,80,60)
        self.assertTrue(mechanism_can_close(*lengths))
        with self.assertRaises(RuntimeError):
            solve_position(lengths,np.pi,self.f['F'],np.radians([45,90]))

    def test_singular_state(self):
        with self.assertRaises(np.linalg.LinAlgError):
            solve_velocity((100,50,100,50),(0,0,0),1,self.f['J'])

    def test_geometric_checks(self):
        self.assertTrue(check_grashof(*LENGTHS))
        self.assertTrue(mechanism_can_close(*LENGTHS))
        self.assertFalse(mechanism_can_close(400,50,100,100))


if __name__ == '__main__':
    unittest.main()
