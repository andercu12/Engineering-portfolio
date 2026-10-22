# Model notes

## Coordinates and equations

The fixed joints are O2 = (0, 0) and O4 = (L1, 0). L2 joins O2 to A, L3 joins A to B, and L4 joins O4 to B. The original code uses theta12, theta23 and theta14 for their absolute orientations.

The loop equations are:

```text
L2*cos(theta2) + L3*cos(theta3) - L4*cos(theta4) - L1 = 0
L2*sin(theta2) + L3*sin(theta3) - L4*sin(theta4)      = 0
```

With q = [theta2, theta3, theta4], the Jacobian is J = dF/dq. Given the input angular velocity and acceleration:

```text
J * q_dot = 0
J * q_ddot + J_dot * q_dot = 0
```

The last two columns of J form the system solved for coupler and rocker rates. SymPy builds the expressions and their derivatives; SciPy solves position and NumPy solves the linear velocity and acceleration systems.

## Assembly branch and singularities

Different starting guesses may select different assembly branches. The previous position is reused as the next initial guess during a sweep. This helps follow a branch but is not a general branch-tracking guarantee near singularities or disconnected feasible angle ranges.

The position solver checks both convergence and a scale-relative loop residual. Velocity and acceleration solvers reject unknown-coordinate Jacobians with condition number above 1e12. That threshold is a numerical guard, not a physical limit.

The link-length closure inequality only indicates that some assembly may be possible; it does not guarantee closure at the requested input angle. Grashof alone also does not guarantee that the chosen input link can rotate fully for every grounding arrangement. Equality can include change-point configurations.

## Animation interpretation

The interactive animation is an angle sweep at a fixed playback interval. It uses the supplied omega2 and alpha2 to calculate instantaneous rates at each sampled configuration, but does not integrate a time law. In particular, nonzero alpha2 does not update omega2 during this sweep.

The separate example exporter uses constant omega2 = 2 rad/s and alpha2 = 0, so its time axis follows theta2(t) = theta2_initial + omega2*t. Its GIF illustrates that same example.

Unreachable or singular states are labelled in the interactive animation rather than displaying a stale configuration. The trajectory is broken across those states and cleared on each repeat.

## What was checked

Five tests cover full-cycle closure and constant link lengths, finite-difference checks of velocity and acceleration with nonzero input acceleration, unreachable angles, a singular state and basic geometric validation. These checks support the supplied examples; they do not establish robustness for all possible linkage geometries.

This is a kinematic model of rigid planar links and ideal joints. It does not calculate forces, motor torque, flexibility, friction or collisions.
