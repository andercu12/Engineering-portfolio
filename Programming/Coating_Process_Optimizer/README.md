# Coating Process Optimizer

I built this project to practise using Python for an engineering problem: choosing mass flow, travel speed and the number of passes to approach a target coating thickness without spending unnecessary time.

The model is deliberately simple. It assumes uniform deposition, a fixed efficiency for each material and constant machine power. It is an exercise in modelling and optimization, not a calibrated coating process.

![Comparison of the three methods](results/comparison.png)

## What it does

The program compares:

- **Coarse grid:** tries a small set of mass flows, speeds and pass counts.
- **Fine grid:** searches more closely around the coarse result.
- **Local optimization:** uses SciPy's L-BFGS-B for mass flow and speed, separately for each integer pass count.

It reports predicted thickness, thickness error, travel time, energy and the objective score. It also saves a CSV table and a comparison plot.

## Running it

Use Python 3.10 or newer. From this folder:

```bash
python -m pip install -r requirements.txt
python src/main.py
```

Enter the target thickness, coating length, spray width and material when prompted. On Windows, `py` can replace `python`.

To run the example used in the plot:

```bash
python src/main.py --example
```

To save the figure without opening a window:

```bash
python src/main.py --example --no-show
```

Outputs go to `results/` and replace the previous comparison. Use `--output results/my_case` to keep a separate run.

## Example

For Al2O3, a target thickness of 0.5 mm, a length of 1000 mm and a width of 10 mm:

| Method | Predicted thickness [mm] | Travel time [s] | Score |
|---|---:|---:|---:|
| Coarse grid | 0.522152 | 25.000 | 0.047624 |
| Fine grid | 0.500703 | 22.222 | 0.012151 |
| Local L-BFGS-B | 0.499347 | 17.931 | 0.002784 |

These are calculated results from the simplified model, not measurements. The local result allows a small thickness error to reduce time. Lower score is better; the score does not enforce an exact target or a hard tolerance.

[Example details](examples/example.md) · [Model and objective](docs/methodology.md)

## A few limitations

- Material efficiencies are illustrative and are not fitted to experimental data.
- Travel time excludes acceleration, turnarounds, setup and cooling.
- Energy is power multiplied by time. At constant power it does not add an independent optimization goal.
- Length changes time and energy, but cancels out of the uniform thickness equation. With the current normalization, it also does not change the optimal settings.
- Fine grid is a neighbourhood search. L-BFGS-B is local; neither is a general guarantee of a global optimum.
- The reported ±0.1 mm tolerance is a result label, not a hard constraint.

## Files

- `src/main.py`: inputs, objective, search methods and output.
- `src/process_model.py`: thickness, time and energy calculations.
- `src/materials.py`: material data.
- `src/config.py`: bounds, grids, weights and machine power.
- `src/visualization.py`: the comparison figure.
- `examples/`: one worked example.
- `tests/`: a few checks for units and optimization results.

Run the checks with:

```bash
python -m unittest discover -s tests -v
```

Next, I would improve the deposition model using measured data and add setup or turnaround time. That would make the process assumptions more useful than adding another optimization algorithm.
