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
| `ga.py` | binary-coded GA (8 bits per ply, invalid codes rejected): initial population, roulette selection, crossover, mutation per gene, elitism |
| `plots.py` | convergence curve and polar diagrams of Q, A\*, B\*, D\* (SVG + PDF + PNG) |
| `main.py` | runs the optimisation and writes everything to `results/` |
| `tests/` | checks against the course values (mechanics, cost) and of the GA operators |

## Usage

`python` on this machine may point to Python 2.7 (Amesim). Use Python 3.12:

The virtual environment lives at the repository root (`.venv/`, ignored by
git); the code lives in this folder. From the repository root:

```bash
py -3.12 -m venv .venv
.venv/Scripts/python -m pip install -r "fonctions/requirements.txt"
cd "fonctions"
../.venv/Scripts/python -m pytest
../.venv/Scripts/python main.py
```

Outputs (in `results/`, not versioned):

- `ga_statistics.csv`: per generation, min / mean / median / max / std of the cost,
  number of rejected genes and best stacking (`;` separator, UTF-8 with BOM)
- `best_laminate.txt`: best stacking sequence and its polar parameters
- `convergence.svg/.pdf/.png`, `polar_diagrams.svg/.pdf/.png`

Options: `--crossover two_point`, `--seed 3`.

## Decisions

- Phi1 uses the slide 45 formula with B\* = 2B/h^2. The value printed on P2
  slide 51 (3.5873e-6) is exactly n^2 = 36 times ours (9.9648e-8): treated as a
  numerical slip on the slide (see `tests/test_fitness.py`).
- "R1-orthotropy in bending" is read as R1(D\*) = 0, i.e. Phi9.
- The 76 codes without an angle are handled by rejection (see `ga.py`).
