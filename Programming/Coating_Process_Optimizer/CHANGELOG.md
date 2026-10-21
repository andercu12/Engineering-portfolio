# Changes for the first runnable release

- Fixed the material dictionary syntax and material function calls.
- Replaced unused `config.txt` with an imported `config.py`.
- Kept coarse grid, fine grid and local L-BFGS-B, with integer pass enumeration.
- Replaced clipped absolute thickness error with scaled squared error. This is a deliberate objective change, so scores differ from the original version.
- Replaced fixed time/energy normalization ranges with bounds from the current model. Previously, energy stayed below the 0.2 kWh normalization minimum throughout the allowed input range and its normalized contribution was always zero.
- Made the dependence between time and energy explicit.
- Checked optimizer success and retained the coarse seed as a fallback.
- Included the coarse seed exactly in fine search and made elapsed-time reporting consistent.
- Added a small plot, CSV output and a reproducible example command.
- Removed unused imports and the tabulate dependency; kept plain console output.
- Added five model and optimization tests and short English documentation.
