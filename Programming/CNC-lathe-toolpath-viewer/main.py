"""SIMPLE EXTERNAL TURNING TOOLPATH VIEWER v1.0

Assumptions: mm, absolute coordinates, X as diameter, and stock between Z=-L and Z=0.
Only the material removed by G1 longitudinal passes at a constant X is calculated.
"""

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parent
CODE_PATH = ROOT / "G-code" / "code.nc"


@dataclass
class CNCCommand:
    """Data listed on a single line. “None” means that the data is not present."""

    line_number: int
    function: Optional[int] = None
    x: Optional[float] = None
    z: Optional[float] = None
    feedrate: Optional[float] = None
    end_program: bool = False


@dataclass
class MachineState:
    """Position and active values of the in-line tool."""

    x: Optional[float] = None
    z: Optional[float] = None
    motion_mode: Optional[int] = None
    feedrate: Optional[float] = None


@dataclass
class Cylinder:
    """A diameter per interval between two consecutive values of Z."""

    initial_diameter: float
    length: float
    limits: list = field(default_factory=list)
    diameters: list = field(default_factory=list)


def ask_value(message):
    """Request a positive dimension; repeat if it is invalid."""
    while True:
        try:
            value = float(input(message))
            if math.isfinite(value) and value > 0:
                return value
        except ValueError:
            pass
        print("Introduce a positive number, for example 50 o 50.5.")


def load_commands():
    """Read a single file as the first step before adding a selector."""
    text = CODE_PATH.read_text(encoding="utf-8-sig")
    return parse_commands(text)


def parse_commands(text):
    """Read words separated by spaces: G01 X30 Z-20 F0.12."""
    commands = []
    for number, raw_line in enumerate(text.splitlines(), 1):
        # Eliminate comments leaving the coordinate negative sign.
        line = raw_line.split(";", 1)[0]
        line = re.sub(r"\([^()]*\)", "", line).strip().upper()
        if not line or line == "%" or re.fullmatch(r"O\d+", line):
            continue

        command = CNCCommand(line_number=number)
        seen = set()
        g_code = None
        for word in line.split():
            if not re.fullmatch(r"[NGXZFSMT][+-]?(?:\d+(?:\.\d*)?|\.\d+)", word):
                raise ValueError(f"Line {number}: invalid word '{word}'. Separate words with spaces.")
            letter = word[0]
            value = float(word[1:])
            if not math.isfinite(value):
                raise ValueError(f"Line {number}: non finite number.")
            if letter in seen:
                raise ValueError(f"Line {number}: this version supports only one word {letter}.")
            seen.add(letter)
            if letter in "NGMT" and (value < 0 or not value.is_integer()):
                raise ValueError(f"Line {number}: {letter} must be a non-negative integer.")

            if letter == "G":
                g_code = int(value)
                if g_code in (0, 1):
                    command.function = g_code
                elif g_code not in (50, 96, 97):
                    raise ValueError(f"Line {number}: G{g_code} it is not implemented.")
            elif letter == "X":
                command.x = value
            elif letter == "Z":
                command.z = value
            elif letter == "F":
                if value <= 0:
                    raise ValueError(f"Line {number}: progress must be positive.")
                command.feedrate = value
            elif letter == "M":
                if value not in (3, 4, 5, 8, 9, 30):
                    raise ValueError(f"Line {number}: M{int(value)} it is not implemented.")
                command.end_program = value == 30
            # N, S and T are known, but do not modify the geometry.

        # G50 limits rpm, but is not accepted with coordinates
        if g_code in (50, 96, 97) and (command.x is not None or command.z is not None):
            raise ValueError(f"Line {number}: spindle block with coordinates not supported.")
        if g_code == 50 and "S" not in seen:
            raise ValueError(f"Line{number}: only G50 S... is recognized as spindle information.")
        commands.append(command)
        if command.end_program:
            break
    return commands


def create_cylinder(diameter, length, commands):
    """Cut the cylinder at the Z-coordinate positions specified by the program."""
    cylinder = Cylinder(diameter, length)
    cylinder.limits = [-length, 0.0]
    for command in commands:
        if command.z is not None and -length < command.z < 0:
            cylinder.limits.append(command.z)
    cylinder.limits = sorted(set(cylinder.limits))
    for _ in range(len(cylinder.limits) - 1):
        cylinder.diameters.append(diameter)
    return cylinder


def simulate(commands, cylinder):
    """Update the tool and reduce the diameters of the sections."""
    state = MachineState()
    movements = []
    warnings = []
    for command in commands:
        if command.function is not None:
            state.motion_mode = command.function
        if command.feedrate is not None:
            state.feedrate = command.feedrate
        if command.x is None and command.z is None:
            continue

        # First, save the previous position; then, get the destination.
        old_x, old_z = state.x, state.z
        new_x = state.x if command.x is None else command.x
        new_z = state.z if command.z is None else command.z
        if new_x is None or new_z is None or state.motion_mode is None:
            raise ValueError("The first positioning command must specify G0, X, and Z.")
        if new_x < 0:
            raise ValueError(f"Line {command.line_number}: X negative not accepted.")

        if old_x is None or old_z is None:
            if state.motion_mode != 0:
                raise ValueError("The first position should be G0.")
            # No inventamos una trayectoria desde un origen desconocido.
            if -cylinder.length <= new_z <= 0 and new_x < cylinder.initial_diameter:
                raise ValueError("The first position is within the raw cylinder.")
            state.x, state.z = new_x, new_z
            continue

        if state.motion_mode == 1:
            if state.feedrate is None:
                raise ValueError(f"Line {command.line_number}: F remains to be defined.")
            if new_x != old_x and new_z != old_z:
                raise ValueError(f"Line {command.line_number}: cones will be added in another version.")
            # Z cut cannot extend beyond the rear end.
            if new_z != old_z and min(new_z, old_z) < -cylinder.length:
                raise ValueError(f"Line {command.line_number}: the pass reaches Z={min(new_z, old_z)} "
                                 f"and the cylinder ends at Z={-cylinder.length}.")

        low_z = min(old_z, new_z)
        high_z = max(old_z, new_z)
        removed = False
        intersects = False
        for i in range(len(cylinder.diameters)):
            start = cylinder.limits[i]
            end = cylinder.limits[i + 1]
            centre = (start + end) / 2
            if low_z < centre < high_z:
                intersects = True
                if state.motion_mode == 1:
                    # Only a longitudinal path with a constant X reaches this point.
                    if new_x < cylinder.diameters[i]:
                        cylinder.diameters[i] = new_x
                        removed = True
                else:
                    # Point-based approach: warning—this is not a full collision detector.
                    fraction = (centre - old_z) / (new_z - old_z)
                    rapid_x = old_x + fraction * (new_x - old_x)
                    if rapid_x < cylinder.diameters[i]:
                        warnings.append(f"Line {command.line_number}: G0 could penetrate material.")
                        break

            # An inward radial motion would require shaping the tool.
            if old_z == new_z and start <= new_z <= end and new_x < old_x:
                if new_x < cylinder.diameters[i]:
                    if state.motion_mode == 1:
                        raise ValueError(f"Line {command.line_number}: radial cut not implemented.")
                    warnings.append(f"Line {command.line_number}: radial G0 might cut into the material.")
                    break

        if state.motion_mode == 1 and intersects and not removed:
            warnings.append(f"Line {command.line_number}: passed through without a reduction in diameter; check the raw cylinder to see if this was unintentional.")
        # A tuple stores the mode and endpoints for later plotting.
        movements.append((state.motion_mode, old_z, old_x, new_z, new_x))
        state.x, state.z = new_x, new_z
    return movements, warnings


def draw_result(cylinder, movements):
    """Separate the part and the path so that the cuts do not reduce the level of detail."""
    fig, (part_ax, path_ax) = plt.subplots(2, 1, figsize=(10, 8))
    for i, diameter in enumerate(cylinder.diameters):
        start = cylinder.limits[i]
        length = cylinder.limits[i + 1] - start
        part_ax.add_patch(Rectangle((start, -diameter / 2), length, diameter,
                                    facecolor="steelblue", edgecolor="black", alpha=0.6))
    part_ax.add_patch(Rectangle((-cylinder.length, -cylinder.initial_diameter / 2),
                                cylinder.length, cylinder.initial_diameter,
                                fill=False, edgecolor="red", linestyle="--"))
    part_ax.set_xlim(-cylinder.length * 1.05, cylinder.length * 0.05)
    part_ax.set_ylim(-cylinder.initial_diameter * 0.6, cylinder.initial_diameter * 0.6)
    part_ax.set_title("Remaining piece and initial block (red)")
    for mode, z0, x0, z1, x1 in movements:
        color = "darkorange" if mode == 0 else "steelblue"
        style = "--" if mode == 0 else "-"
        path_ax.plot([z0, z1], [x0 / 2, x1 / 2], color=color, linestyle=style)
    path_ax.set_title("Complete trajectory: G0 orange; G1 blue")
    path_ax.margins(0.1)
    for axis in (part_ax, path_ax):
        axis.set_xlabel("Z [mm]")
        axis.set_ylabel("Radial Position X/2 [mm]")
        axis.set_aspect("equal", adjustable="box")
        axis.grid(True)
    fig.tight_layout()
    plt.show()


def main():
    """Follow these steps: read, define the raw cylinder, simulate, display, and draw."""
    print("\n====================================")
    print("SIMPLE EXTERNAL TURNING TOOLPATH VIEWER ")
    print("====================================")
    print("Assumptions: mm, absolute, X in diameter; Z=0 on the front face.")
    print("G50/G96/G97, S, T, and spindle/coolant auxiliary commands are not simulated.")
    commands = load_commands()
    if not commands:
        print("The file does not contain any instructions.")
        return
    diameter = ask_value("Initial diameter [mm] (example: 50): ")
    length = ask_value("Initial longitude [mm] (example: 60): ")
    cylinder = create_cylinder(diameter, length, commands)
    movements, warnings = simulate(commands, cylinder)
    for warning in warnings:
        print("WARNING:", warning)
    print("\nStart Z | Final Z | Remaining diameter [mm]")
    for i, diameter in enumerate(cylinder.diameters):
        print(f"{cylinder.limits[i]:8.2f} | {cylinder.limits[i+1]:7.2f} | {diameter:.2f}")
    if all(d == cylinder.initial_diameter for d in cylinder.diameters):
        print("WARNING: No material has been removed. Check the dimensions and schedule.")
    draw_result(cylinder, movements)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, UnicodeError, EOFError, KeyboardInterrupt) as error:
        print(f"Program suspended: {error}")
