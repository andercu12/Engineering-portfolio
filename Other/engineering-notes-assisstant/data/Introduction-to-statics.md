# Introduction to Statics

Engineering Statics is the gateway into engineering mechanics, which applies
Newtonian physics to design and analyze objects, systems, and structures with
respect to motion, deformation, and failure.

Statics is concerned with particles and rigid bodies in equilibrium. These
bodies may be at rest or moving with constant velocity. The knowledge gained in
Statics is used in later engineering courses, especially Dynamics, Mechanics of
Solids, and Fluid Mechanics.

## Newton's Laws of Motion

Sir Isaac Newton laid the foundation of mechanics in 1687 with his three laws of
motion, which describe the relationship between forces, objects, and motion.

Motion can be classified into two types:

- **Translation:** a body changes position without changing its orientation.
- **Rotation:** a body spins about an axis without changing its average position.

### Newton's First Law

Newton’s first law states that an object remains at rest or in uniform motion in
a straight line unless acted upon by a net external force. This is also called
the **law of inertia**.

The same idea applies to rotation. A force can create a rotational tendency
called a **moment** or **torque**. Just as a net force changes linear velocity,
a net moment changes angular velocity.

### Newton's Second Law

Newton’s second law is:

\[
\vec{F} = m\vec{a}
\]

Where:

- \( \vec{F} \) is the net force.
- \( m \) is the mass.
- \( \vec{a} \) is the acceleration.

Force and acceleration are vector quantities; mass is a scalar quantity.

In Statics, bodies do not accelerate. Therefore:

\[
\vec{a} = 0
\]

\[
\sum \vec{F} = 0
\]

For planar rotation about a fixed axis with constant moment of inertia
about that axis (a scalar relation, not a general 3D vector equation):

\[
\sum M_{axis} = I_{axis}\alpha
\]

Where:

- \( \vec{M} \) is the net moment.
- \( I \) is the mass moment of inertia.
- \( \vec{\alpha} \) is the angular acceleration.

For a body in static equilibrium:

\[
\vec{\alpha} = 0
\]

\[
\sum \vec{M}_O = 0
\]

### Newton's Third Law

Newton’s third law states that for every action there is an equal and opposite
reaction. Forces always occur in pairs: if body \(A\) exerts a force on body
\(B\), then body \(B\) exerts an equal and opposite force on body \(A\).

Statics problems usually begin with a **free-body diagram (FBD)**. An FBD
isolates a body or system and shows all external forces and moments acting on
it.

## Units

A numerical value must include its unit, unless the quantity is dimensionless.

The SI system is based on seven base units. The most important base units in
Statics are mass, length, and time.

- Acceleration:

\[
a = \frac{L}{t^2}
\]

- Force:

\[
F = ma
\]

Therefore, force has units of:

\[
\text{kg} \cdot \text{m/s}^2 = \text{N}
\]

### Unit Systems

| Unit system | Force | Mass | Length | Time | \(g\) on Earth |
|---|---:|---:|---:|---:|---:|
| International System (SI) | N | kg | m | s | \(9.81\ \text{m/s}^2\) |
| British Gravitational | lbf | slug | ft | s | \(32.2\ \text{ft/s}^2\) |
| English Engineering | lbf | lbm | ft | s | \(32.2\ \text{ft/s}^2\) |

In the SI system:

\[
1\ \text{N} = 1\ \text{kg} \cdot \text{m/s}^2
\]

In the British Gravitational system:

\[
1\ \text{lbf} = 1\ \text{slug} \cdot \text{ft/s}^2
\]

The conversion between mass units is:

\[
1\ \text{slug} = 32.174\ \text{lbm} = 14.59\ \text{kg}
\]

### Avoiding Common Unit Errors

- Always check the units of every quantity.
- Use a consistent unit system throughout the problem.
- Add or subtract only quantities with the same units.
- Apply unit operations when multiplying or dividing quantities.
- Verify that both sides of an equation have the same units.
- Check whether the final answer is reasonable in magnitude, units, and direction.

The relationship among weight, mass, and gravitational acceleration is:

\[
W = mg
\]

Where \(W\) is weight, \(m\) is mass, and \(g\) is gravitational acceleration.

## Forces

- **Point forces** or **concentrated forces** act at a single point. They are an
  idealization, since real forces act over an area.
- **Distributed forces** are spread over a line, area, or volume.
- **Body forces** act throughout the volume of a body. Weight is the most common
  example.
- **Loads** are forces that a structure must support to perform its function.
- **Reaction forces** are forces and moments provided by supports to constrain a
  body and maintain equilibrium.
- **Interaction forces** occur between connected bodies and obey Newton’s third
  law.
- **Internal forces** act within a body to resist external loads. They are
  commonly modeled as axial force, shear force, and bending moment.

## Problem Solving

To solve Statics problems effectively:

- Strengthen algebra, trigonometry, and calculus skills.
- Learn the terminology used in engineering mechanics.
- Understand the assumptions behind every equation.
- Practice many problems independently.
- Draw clear, labeled free-body diagrams.
- Check results for magnitude, units, signs, and physical meaning.

For equilibrium problems, follow these steps:

1. Read and understand the problem.
2. Identify the given information and the unknowns.
3. Plan a solution strategy.
4. Draw a complete free-body diagram.
5. Choose a coordinate system.
6. Apply the equilibrium equations.
7. Solve for the unknowns.
8. Check the magnitude, units, and direction of each result.

For a 2D rigid body, the equilibrium equations are:

\[
\sum F_x = 0
\]

\[
\sum F_y = 0
\]

\[
\sum M_O = 0
\]
