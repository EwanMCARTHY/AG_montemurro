# AG_montemurro

Projet EVCSP (ENSAM, 3A) : algorithme génétique écrit en Python (NumPy et
Matplotlib) qui cherche l'empilement d'un stratifié carbone/époxyde ayant les
symétries élastiques demandées, exprimées avec la méthode polaire de G. Verchery.

## Groupe 1

- 20 plis, orientations dans ]-90°, 90°] au pas de 1°
- Découplage, orthotropie R0 en membrane, symétrie du carré (R1 = 0) en flexion
- Fonction de coût : Φ = Φ1 + Φ4 + Φ9 (P2 slides 45-47)

## Fichiers

| Fichier | Rôle |
|---|---|
| `config.py` | données d'entrée : pli et paramètres de l'AG |
| `laminate.py` | S, Q, Q(δ), puis A\*, B\*, D\*, C\* (voie cartésienne) |
| `polar.py` | paramètres polaires, norme, composante L11(θ) |
| `fitness.py` | fonction de coût Φ1 + Φ4 + Φ9 et fitness |
| `ga.py` | codage sur 8 bits (codes invalides rejetés), sélection, croisement, mutation, élitisme |
| `plots.py` | courbe de convergence et diagrammes polaires (PNG) |
| `main.py` | lance le calcul et écrit les résultats |

## Utilisation

Depuis la racine du dépôt (Python 3.12 ; `python` peut pointer vers le Python 2.7 d'Amesim) :

```bash
py -3.12 -m venv .venv
.venv/Scripts/python -m pip install -r fonctions/requirements.txt
cd fonctions
../.venv/Scripts/python main.py --seed 1
```

Résultats dans `results/seed_<graine>/` (non versionné) : `ga_statistics.csv`,
`convergence.png`, `polar_diagrams.png`.

## Choix

- Φ1 suit la formule de la slide 45 avec B\* = 2B/h². La valeur affichée sur
  la slide 51 vaut exactement n² = 36 fois la nôtre : considérée comme une
  erreur d'application numérique.
- « Orthotropie R1 en flexion » : coquille de l'énoncé, confirmée par le prof ;
  il faut lire R1(D\*) = 0, soit Φ9.
- Les 76 codes sans angle sont rejetés (voir `ga.py`).
