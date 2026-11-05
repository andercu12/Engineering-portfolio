# Support Models and Reactions in 2D

## 1. Purpose of Supports

A support constrains the motion of a structure or rigid body. In return, the
support applies a **reaction** on the body.

The basic rule is:

\[
\text{Movement prevented} = \text{Reaction created}
\]

- If a support prevents translation in a direction, it produces a reaction force
  in that direction.
- If a support prevents rotation, it produces a reaction moment or couple.

In 2D, a rigid body has three possible motions:

- Translation in the \(x\)-direction
- Translation in the \(y\)-direction
- Rotation about the \(z\)-axis

Therefore, a 2D support can transmit at most three independent reaction
components: \(F_x\), \(F_y\), and \(M\).

## 2. Main Types of Supports

| Support model | Prevents | Allows | Reactions transmitted | Unknowns |
|---|---|---|---|---|
| Roller, rocker, or smooth surface | Translation perpendicular to the surface | Translation parallel to the surface and rotation | One normal force | 1 |
| Pin or hinge | Translation in \(x\) and \(y\) | Rotation | Two force components: \(A_x\), \(A_y\) | 2 |
| Fixed support | Translation in \(x\) and \(y\), and rotation | Nothing | Two force components and one moment: \(A_x\), \(A_y\), \(M_A\) | 3 |
| Cable | Separation along the cable direction | Movement perpendicular to the cable | Tension along the cable | 1 |
| Two-force link | Relative movement along the link axis | Rotation at its connections | Force along the axis of the link | 1 |
| Smooth collar on a rod | Movement perpendicular to the rod | Sliding along the rod and rotation | One force perpendicular to the rod | 1 |
| Fixed collar on a rod | Movement perpendicular to the rod and rotation | Sliding along the rod | One perpendicular force and one moment | 2 |
| Rough surface with friction | Penetration; sliding if friction is sufficient | Rolling or limited sliding, depending on friction | Normal force and friction force | 2 |

## 3. Roller Support

A roller support prevents movement only in the direction perpendicular to the
supporting surface. It allows translation parallel to the surface and rotation.

For a horizontal roller support:

\[
R_y \text{ is an unknown and may be zero}
\]

\[
R_x = 0
\]

\[
M = 0
\]

The reaction force is always **normal** to the contact surface.

Examples:

- Bridge expansion bearings
- Wheels or rollers
- Smooth contact surfaces

## 4. Pin or Hinge Support

A pin support prevents horizontal and vertical translation at the connection
point, but it allows free rotation.

It transmits:

\[
A_x
\]

\[
A_y
\]

It does **not** transmit a reaction moment:

\[
M_A = 0
\]

The two force components may also be combined into one resultant force:

\[
A = \sqrt{A_x^2 + A_y^2}
\]

Examples:

- Door hinges
- Truss joints
- Simple beam supports

## 5. Fixed Support

A fixed support, also called a built-in or cantilever support, prevents both
translation and rotation.

It transmits:

\[
A_x
\]

\[
A_y
\]

\[
M_A
\]

Therefore, it provides **three reaction unknowns** in 2D.

Examples:

- A beam embedded in a wall
- A cantilever balcony
- A welded beam-column connection

## 6. Cable Support

A cable can only pull, not push. Therefore, it transmits a tensile force along
its own line of action.

\[
\vec{T} = T\hat{u}
\]

Where \( \hat{u} \) is the unit vector along the cable, pointing away from the
body.

A cable provides:

- One unknown: the tension \(T\)
- A force directed along the cable
- No moment reaction

## 7. Link Support

A two-force link is a member connected at only two points, with no external load
applied between those points.

The reaction is a force directed along the line joining the two connection
points.

\[
\vec{F} = F\hat{u}_{link}
\]

A link provides:

- One unknown force
- A force along the axis of the link
- No moment reaction

## 8. Smooth Collar on a Rod

A smooth collar can slide along a rod but cannot move perpendicular to it.

It transmits:

- One reaction force perpendicular to the rod
- No friction force, assuming the rod is smooth
- No moment reaction

If the collar is fixed to the member, it may also transmit a reaction moment.

## 9. Rough Surface

A rough contact can resist penetration and may prevent sliding while static
friction is sufficient. It cannot resist separation without another restraint.

It transmits:

- A normal force \(N\), perpendicular to the surface
- A friction force \(f\), parallel to the surface

\[
R = \sqrt{N^2 + f^2}
\]

The friction force opposes the tendency of relative sliding.

## 10. Number of Unknowns and Stability

In 2D, three independent equilibrium equations are available:

\[
\sum F_x = 0
\]

\[
\sum F_y = 0
\]

\[
\sum M_O = 0
\]

Therefore:

- A structure with exactly three unknown reaction components can generally be
  solved using equilibrium equations alone.
- A common stable arrangement is one pin support plus one roller support.
- A single fixed support can also provide three reaction components.
- If there are more than three unknowns, additional equations or conditions are
  required.
- If the reactions cannot prevent all rigid-body motions, the structure is
  unstable.

## 11. Example: Beam with Pin and Roller

A horizontal beam has a pin support at \(A\) and a roller support at \(B\).

The pin at \(A\) provides:

\[
A_x,\quad A_y
\]

The roller at \(B\), on a horizontal surface, provides:

\[
B_y
\]

Total unknowns:

\[
A_x,\ A_y,\ B_y
\]

For this stable arrangement with distinct support positions, the three
independent equilibrium equations can determine the three reactions. Counting
unknowns alone does not establish stability.

## 12. Key Points

- A reaction exists only in a direction or rotation that the support prevents.
- Rollers provide one normal reaction force.
- Pins provide two force components but no moment.
- Fixed supports provide two force components and one moment.
- Cables and two-force links provide one force along their axis.
- The support reactions are external forces and moments in the free-body diagram.
- Correctly identifying support reactions is essential before applying the
  equilibrium equations.
