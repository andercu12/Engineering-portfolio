"""Default settings for the simplified coating model."""
MACHINE_POWER_KW = 2.5
MASS_FLOW_GRID = [0.50, 1.00, 1.25, 1.50, 2.00]  # g/s
SPEED_GRID = [30.0, 40.0, 50.0, 60.0]  # mm/s
PASSES = [1, 2, 3, 4, 5, 6]
MIN_MASS_FLOW, MAX_MASS_FLOW = 0.50, 2.00
MIN_SPEED, MAX_SPEED = 30.0, 60.0
FINE_MASS_FLOW_MARGIN = 0.30
FINE_SPEED_MARGIN = 5.0
FINE_GRID_POINTS = 100
WEIGHT_THICKNESS = 0.60
WEIGHT_TIME = 0.30
WEIGHT_ENERGY = 0.10
THICKNESS_ERROR_SCALE_MM = 0.10  # A score scale, not a hard constraint.
THICKNESS_TOLERANCE_MM = 0.10  # Used to label the reported result.
