O0002 (TURNING 3 DIAMETERS)
(--------------------------------------------------)
(TOOL 1: EXTERNAL ROUGHING)
(--------------------------------------------------)
N10 T0101           (Selects Tool 1 and its corrector)
N15 G96 S180 M03    (Constant cutting speed 180 m/min, clockwise rotation)
N20 G50 S2500       (Limits the maximum RPM to 2500 for safety.)
N25 G00 X55.0 Z2.0 M08 (Rapid approach to a safe zone and coolant source)

(--- ROUGHING PASSES FOR THE SECTION OF Ø40 ---)
N30 G00 X46.0       (Positioning for the 1st pass)
N35 G01 Z-45.0 F0.25 (Longitudinal displacement up to Z-45)
N40 G01 X48.0       (It is removed at X, outside the material.)
N45 G00 Z2.0        (Quick return to initial Z)

N50 G00 X42.0       (Positioning for the 2nd pass)
N55 G01 Z-45.0      (Longitudinal displacement)
N60 G01 X44.0       (Removed at X)
N65 G00 Z2.0        (Quick return)

N70 G00 X40.4       (Final pass leaving 0.4mm for finishing)
N75 G01 Z-45.0
N80 G01 X45.0
N85 G00 Z2.0

(--- ROUGHING PASSES FOR THE SECTION OF Ø30 ---)
N90 G00 X36.0       (Go down to next level, length Z-20)
N95 G01 Z-20.0
N100 G01 X38.0
N105 G00 Z2.0

N110 G00 X32.0
N115 G01 Z-20.0
N120 G01 X34.0
N125 G00 Z2.0

N130 G00 X30.4      (Final pass leaving 0.4mm for finishing)
N135 G01 Z-20.0
N140 G01 X42.0      (Step up to clear the step)
N145 G00 Z5.0       (Safe roughing retraction)

(--------------------------------------------------)
(ROUGHING PASSES WITH SAME TOOL OR ONE FOR FINISHING)
(--------------------------------------------------)
(Note: Se reduce el avance F para mejorar el acabado superficial)
N150 G00 X26.0 Z2.0 (Quick approach)
N155 G00 X30.0      (Positioned at the final Ø of the tip)
N160 G01 Z-20.0 F0.12 (Cylinder Section 1 to Ø30 with fine advance)
N165 G01 X40.0      (Move up to Ø40)
N170 G01 Z-45.0     (Turning Section 2 to Ø40)
N175 G01 X52.0      (Move upward while cleaning the last face of the material)

(--------------------------------------------------)
(PROGRAM END)
(--------------------------------------------------)
N180 G00 X150.0 Z150.0 M09 (Retirada rápida al punto de cambio y apaga refrigerante)
N185 M05            (Parada del husillo)
N190 M30            (End of program and restart)