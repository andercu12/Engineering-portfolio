# Four-Bar Mechanism Kinematic Analysis

This project develops a Python-based tool for the kinematic analysis of a planar four-bar linkage.

The mechanism is modelled through nonlinear loop-closure constraint equations. Joint positions are obtained numerically, while velocities and accelerations are calculated using the Jacobian of the constraint system.

Symbolic expressions are generated with SymPy and converted into numerical functions for efficient evaluation with NumPy and SciPy.

The project also includes geometric validation and dynamic visualization of the mechanism motion.

## Main features

- Four-bar linkage geometric model.

- Loop-closure constraint equations.

- Numerical position analysis.

- Jacobian-based velocity analysis.

- Jacobian-based acceleration analysis.

- Grashof and geometric feasibility checks.

- Joint trajectory calculation.

- Angular velocity and acceleration results.

- Animated mechanism visualization.

- Modular Python architecture prepared for extension to more complex mechanisms.

## Technologies

Python · NumPy · SciPy · SymPy · Matplotlib
