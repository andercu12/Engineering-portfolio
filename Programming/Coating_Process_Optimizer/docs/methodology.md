# Model and objective

## Thickness

The mass flow is in g/s, speed in mm/s and spray width in mm. Density is converted from g/cm³ to g/mm³ by dividing by 1000.

For a constant deposition efficiency eta and N passes:

```text
thickness = mass_flow * eta * N / (density * speed * width)
```

This assumes a uniform deposited layer over a single track. The model does not describe temperature, particle flight, adhesion, porosity or overlapping tracks.

| Material | Density [g/cm³] | Assumed efficiency |
|---|---:|---:|
| Al2O3 | 3.95 | 0.55 |
| YSZ | 6.0 | 0.50 |
| NiCr | 8.2 | 0.65 |

These are illustrative model inputs, not a process qualification dataset.

## Time and energy

```text
time_s = length_mm / speed_mm_s * passes
energy_kwh = power_kw * time_s / 3600
```

Power is fixed at 2.5 kW. The time calculation represents travel only. For a longer track, deposited mass and coated area grow proportionally, so the calculated thickness stays unchanged.

## Objective function

```text
score = 0.60 * ((thickness - target) / 0.10)^2
      + 0.30 * normalized_time
      + 0.10 * normalized_energy
```

Time is normalized using the fastest and slowest settings allowed for the current length:

```text
t_min = length / max_speed * min_passes
t_max = length / min_speed * max_passes
normalized_time = (time - t_min) / (t_max - t_min)
```

Energy uses the corresponding energy bounds. At constant power, normalized energy equals normalized time exactly. The current weights therefore act as 0.60 for scaled squared thickness error and 0.40 for normalized time. Both terms are retained to make this relationship visible and keep the original three-term structure.

The error term is not clipped. Values over 0.1 mm remain distinguishable, and the squared expression is smooth for local optimization. The scale 0.1 mm controls the trade-off; it is not an enforced limit. A separate output field indicates whether absolute error is within ±0.1 mm.

Normalizing by the current length makes scores comparable within a run, but also removes length from the optimization decision. Scores should not be interpreted as physical cost or compared across different model definitions.

## Search methods

Mass flow is bounded between 0.5 and 2 g/s, speed between 30 and 60 mm/s, and passes are integers from 1 through 6.

The coarse search tries 5 mass flows, 4 speeds and 6 pass counts (120 combinations). Fine search uses a neighbourhood of ±0.3 g/s and ±5 mm/s around the coarse winner, clipped to the original bounds. Each axis has 100 evenly spaced samples plus the exact seed when absent. All pass counts are tested again. Keeping the seed ensures that fine search cannot return a worse score merely because its sampling missed the coarse point.

Local search runs bounded L-BFGS-B once for each pass count, with the coarse solution as its starting point. Only successful finite results are accepted. If a run fails, it is reported; the best successful result or coarse seed remains available.

Elapsed time is measured with `perf_counter`, not CPU time. Coarse-search time is included in both refinement totals, since both need that seed. Plotting and user input are excluded. Single-run timings vary with the machine and are only indicative.

## Checks

The tests cover lookup, mass balance, unit conversion, length scaling, invalid physical inputs and search bounds. The documented local result is compared with an independent one-dimensional reference: for each speed and pass count, solve the exact-thickness mass flow and clip it to the allowed interval, then evaluate the same score over a dense speed grid. This check supports this example, not a global convergence guarantee for every future model.
