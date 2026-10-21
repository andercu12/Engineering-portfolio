# Triangular truss benchmark

Enter the following sequence at the prompts:

```text
(0,0)
(1000,0)
(0,1000)
stop
(0,0)
(1000,0)
(1,2)
(1,3)
(2,3)
(0,0)
(0,0)
(0,1000)
```

Nodes 1 and 2 carry the pinned and roller supports, respectively. All bars have A = 1200 mm² and E = 200000 N/mm².

## Analytical reference

For +1000 N vertically at node 3, only the vertical bar carries force: N2 = 1000 N. Its extension is FL/(AE) = 0.004166666667 mm, and its stress is F/A = 0.833333333333 MPa. Zero first-order extension of the diagonal requires ux3 = uy3. The horizontal displacement is therefore nonzero even though the applied load is vertical.

| Quantity | +1000 N vertical | -1000 N vertical |
|---|---:|---:|
| ux1, uy1 [mm] | 0, 0 | 0, 0 |
| ux2, uy2 [mm] | 0, 0 | 0, 0 |
| ux3 [mm] | 0.004166667 | -0.004166667 |
| uy3 [mm] | 0.004166667 | -0.004166667 |
| Pinned Rx [N] | 0 | 0 |
| Pinned Ry [N] | -1000 | 1000 |
| Roller Ry [N] | 0 | 0 |
| Element 1 stress [MPa] | 0 | 0 |
| Element 2 stress [MPa] | 0.833333333 | -0.833333333 |
| Element 3 stress [MPa] | 0 | 0 |

Change only the final input to `(0,-1000)` for the reverse-load check. Small floating-point residuals are expected. Tests use absolute tolerances of 1e-10 mm / MPa and 1e-8 N for these benchmarks.

## Horizontal-load diagnostic

With `(1000,0)` at node 3, equilibrium instead gives pinned reactions (-1000, -1000) N and roller reaction +1000 N. Bar stresses are +0.833333, +0.833333 and -1.178511 MPa. Node 3 has ux = 0.020118446 mm and uy = 0.004166667 mm; node 2 has ux = 0.004166667 mm.

This case reproduces the previously reported values and verifies that the roller reaction and node-table rows are now indexed correctly.

Actual execution logs are in `../results/`. Compression stresses do not establish buckling resistance.
