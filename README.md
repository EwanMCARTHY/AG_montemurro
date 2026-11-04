# AG_montemurro

EVCSP project (ENSAM, 3rd year): a genetic algorithm (GA), written from
scratch in Python, that searches for the stacking sequence of a
carbon/epoxy laminate with prescribed elastic symmetries. The symmetries are
expressed with G. Verchery's polar method.

- Project statement: `docs/projet_AG.pdf`
- Course: `docs/EVCSP_P1.pdf`, `EVCSP_P2.pdf`, `EVCSP_P3.pdf` (the laminate
  and polar-method slides used here are P2 slides 35-51)

## Group 1

| Item | Value |
|---|---|
| Elastic symmetries | decoupling, R0-orthotropy in membrane, R1 = 0 in bending |
| Number of plies | 20 |
| Cost function | Φ = Φ1 + Φ4 + Φ9 (P2 slides 45-47) |

Ply: E1 = 161 GPa, E2 = 9 GPa, ν12 = 0.26, G12 = 6.1 GPa, t = 0.125 mm.
Orientations in ]-90°, 90°] with a 1° step.

## Code layout

| File | Role |
|---|---|
| `config.py` | all input data: ply, group objectives, GA parameters |
| `laminate.py` | ply compliance S and stiffness Q, rotation, A, B, D, A\*, B\*, D\*, C (Cartesian route) |
| `polar.py` | polar parameters T0, T1, R0, R1, Φ0, Φ1, norm, direct polar sums (slides 41-42) |
| `fitness.py` | partial objectives Φ1-Φ11, cost function, fitness of the statement |
| `ga.py` | binary-coded GA: initial population, roulette selection, crossover, mutation, elitism |
| `plots.py` | convergence curve and polar diagrams (SVG + PDF) |
| `main.py` | runs the optimisation and writes everything to `results/` |
| `tests/` | mechanical checks against the course values |

## Usage

`python` on this machine may point to Python 2.7 (Amesim). Use Python 3.12:

```bash
py -3.12 -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pytest
.venv/Scripts/python main.py
```

Outputs (in `results/`, not versioned):

- `ga_statistics.csv`: population statistics per generation (`;` separator, UTF-8 with BOM)
- `best_laminate.txt`: best stacking sequence and its polar parameters
- `convergence.svg/.pdf`, `polar_diagrams.svg/.pdf`
