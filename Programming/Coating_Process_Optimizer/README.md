# Coating Process Optimizer

This project develops a Python-based optimization tool for a simplified industrial coating process.

The model estimates coating thickness, process time and energy consumption based on process variables such as mass flow rate, travel speed, number of passes and coating material properties.

Several optimization strategies are implemented and compared, including Coarse Grid Search, Fine Grid Search and local numerical optimization using SciPy.

The objective function combines three normalized criteria:

- coating thickness error;

- process cycle time;

- energy consumption.

The project is structured into independent modules for material data, process modelling, optimization and result visualization, with the aim of creating a clear and scalable engineering software architecture.

## Main features

- Material library for Al2O3, YSZ and NiCr.

- Physics-based coating thickness estimation.

- Process time and energy calculation.

- Multi-objective normalized cost function.

- Coarse and refined Grid Search.

- Local numerical optimization.

- Performance benchmark between optimization methods.

- Input validation and structured results.

## Technologies

Python · NumPy · SciPy · Tabulate
