# Equilibrium of Forces and Moments in 2D

## 1. Concept of Equilibrium

A rigid body is in **static equilibrium** when it has:

- No linear acceleration: \( \vec{a} = 0 \)
- No angular acceleration: \( \vec{\alpha} = 0 \)

Static equilibrium additionally assumes that the body is initially at rest.
Zero acceleration alone does not imply zero velocity. Static equilibrium requires both the
resultant force and the resultant moment acting on it are zero.

\[
\sum \vec{F} = 0
\]

\[
\sum \vec{M} = 0
\]

## 2. Equations in Two Dimensions

For a body in the \(xy\)-plane, the equilibrium equations are:

\[
\sum F_x = 0
\]

\[
\sum F_y = 0
\]

\[
\sum M_O = 0
\]

Where:

- \( \sum F_x = 0 \): the sum of all horizontal force components is zero.
- \( \sum F_y = 0 \): the sum of all vertical force components is zero.
- \( \sum M_O = 0 \): the sum of all moments about any point \(O\) is zero.

In 2D, a rigid body has **three independent equilibrium equations**, so it can
generally be solved for up to **three unknowns**.

## 3. Force Components

A force \(F\) can be decomposed into rectangular components:

\[
F_x = F \cos\theta
\]

\[
F_y = F \sin\theta
\]

The magnitude and direction are:

\[
F = \sqrt{F_x^2 + F_y^2}
\]

\[
\theta = \operatorname{atan2}(F_y, F_x)
\]

Sign convention:

- Forces to the right are usually positive in \(x\).
- Forces upward are usually positive in \(y\).
- Forces to the left or downward are negative.

## 4. Moment of a Force

The moment of a force measures its tendency to cause rotation about a point.

\[
M = Fd
\]

Where:

- \(M\) is the moment.
- \(F\) is the magnitude of the force.
- \(d\) is the perpendicular distance from the point to the line of action of the force.

Using vector notation:

\[
\vec{M}_O = \vec{r} \times \vec{F}
\]

In 2D, the moment acts about the \(z\)-axis, perpendicular to the \(xy\)-plane.

Sign convention:

- Counterclockwise moments are usually positive.
- Clockwise moments are usually negative.

## 5. Varignon’s Theorem

The moment of a force about a point is equal to the sum of the moments of its
components about the same point.

\[
M_O = x F_y - y F_x
\]

Where:

- \(x\) and \(y\) are the coordinates of the point of application of the force
  relative to point \(O\).
- \(F_x\) and \(F_y\) are the components of the force.

## 6. Free-Body Diagram

A **free-body diagram (FBD)** shows a body isolated from its surroundings, with
all external forces and moments acting on it.

It should include:

- Applied forces
- Weight \(W = mg\)
- Support reactions
- Applied couples or moments
- Dimensions and angles

### Common support reactions in 2D

| Support | Possible reactions |
|---|---|
| Roller | One perpendicular reaction force |
| Pin / hinge | Two reaction forces: \(A_x\) and \(A_y\) |
| Fixed support | Two reaction forces and one reaction moment |

## 7. Procedure to Solve 2D Equilibrium Problems

1. Choose the body or system to analyze.
2. Draw the free-body diagram.
3. Choose a coordinate system.
4. Resolve all forces into \(x\) and \(y\) components.
5. Apply:

\[
\sum F_x = 0
\]

\[
\sum F_y = 0
\]

6. Choose a convenient point to sum moments.
7. Apply:

\[
\sum M_O = 0
\]

8. Solve the equations for the unknowns.
9. Check the direction and sign of each result.

## 8. Choosing the Moment Center

Choose a point where one or more unknown forces pass through.

This is useful because a force passing through the moment center produces no
moment:

\[
M = Fd = 0
\]

Therefore, those unknown forces disappear from the moment equation, making the
problem easier to solve.

## 9. Example

A beam is subjected to a downward vertical force \(P = 100\ \text{N}\) at a distance
\(L = 2\ \text{m}\) from a pin support \(A\). A roller support \(B\) is located
at the other end, \(4\ \text{m}\) from \(A\).

Find the support reactions.

### Equilibrium equations

\[
\sum M_A = 0
\]

\[
B_y(4) - P(2) = 0
\]

\[
B_y = \frac{100(2)}{4} = 50\ \text{N}
\]

\[
\sum F_y = 0
\]

\[
A_y + B_y - P = 0
\]

\[
A_y = 100 - 50 = 50\ \text{N}
\]

\[
\sum F_x = 0
\]

\[
A_x = 0
\]

### Result

\[
A_x = 0
\]

\[
A_y = 50\ \text{N}
\]

\[
B_y = 50\ \text{N}
\]

## 10. Key Points

- In 2D, equilibrium requires three independent equations.
- Forces must balance in both the \(x\) and \(y\) directions.
- Moments must balance about any chosen point.
- A free-body diagram is essential before writing equations.
- Choosing the best point for the moment equation can simplify the solution.
- A 2D problem can generally determine up to three unknowns.
