# Methodology

Each node has two translational degrees of freedom. Physical labels are one-based: node n uses (2n-1, 2n). NumPy indices are zero-based: node at list position i uses (2i, 2i+1).

The global displacement and force vectors follow `[x1, y1, x2, y2, ...]`. Convert physical DOF labels to array indices exactly once. The node table uses `nodes_dof[n]` when enumerating from zero. The roller Y reaction uses its Y DOF label minus one.

## Element formulation

For endpoints i and j:

$$L=\sqrt{(x_j-x_i)^2+(y_j-y_i)^2},\quad c=(x_j-x_i)/L,\quad s=(y_j-y_i)/L.$$

The element stiffness in global coordinates is

$$k_e=\frac{AE}{L}\begin{bmatrix}c^2&cs&-c^2&-cs\\cs&s^2&-cs&-s^2\\-c^2&-cs&c^2&cs\\-cs&-s^2&cs&s^2\end{bmatrix}.$$

The existing variable name `k_local` is retained, although this 4-by-4 matrix is already expressed in global coordinates. Element contributions are summed into the global matrix using the element DOF indices.

## Boundary conditions

Restrained displacements are zero. Solve `Kff @ uf = Ff` using `numpy.linalg.solve`, then place `uf` back into a zero-initialized full vector at the free indices. Reactions follow `R = K @ u - F`, retaining all applied loads, including loads on supports. Free-DOF entries of R should be approximately zero.

## Axial stress

With `ue = [uxi, uyi, uxj, uyj]`, axial extension is `[-c,-s,c,s] @ ue`; strain is extension/L and stress is E times strain. Positive values indicate tension. Use E = 200000 N/mm² to obtain MPa.

## Verification and limits

The tests compare analytical displacement, reaction and stress results and explicitly verify table-to-vector mapping. Additional cases exercise support loads, node-order changes and unstable geometry. Matrix rank is checked using NumPy's default numerical tolerance; very ill-conditioned geometries may be rejected. Stability is not guaranteed by the element-count condition alone.

This is an educational linear truss model, not a complete member-design or structural certification tool.
