# Le projet AG expliqué depuis zéro

Ce document explique **tout le sujet** comme si tu ne l'avais jamais vu :
la mécanique des composites, la méthode polaire, l'algorithme génétique, et
comment chaque morceau correspond à un fichier du code. Il suit l'ordre
logique : d'abord *qu'est-ce qu'on fabrique*, ensuite *comment on décrit sa
rigidité*, puis *ce qu'on cherche*, et enfin *comment on le cherche*.

---

## 0. Le projet en une phrase

On cherche dans quelles directions orienter les **20 couches de fibres de
carbone** d'une plaque pour qu'elle se comporte mécaniquement d'une façon
précise (imposée par l'énoncé), et on fait chercher ces 20 angles par un
**algorithme génétique**, un programme qui imite l'évolution naturelle.

---

## 1. Qu'est-ce qu'un composite stratifié ?

### 1.1 Le pli

Un **pli** (ou couche) est une feuille très fine (ici **0,125 mm**) faite de :

- **fibres de carbone** toutes parallèles : très rigides et très résistantes
  *dans leur direction* ;
- **résine époxyde** (la « matrice ») qui colle les fibres ensemble : molle.

Conséquence : un pli est **très rigide dans le sens des fibres** et **mou
en travers**. Avec nos valeurs :

| Grandeur | Valeur | Ce que ça veut dire |
|---|---|---|
| E1 = 161 000 MPa | 161 GPa | rigidité en tirant **dans le sens des fibres** (proche de l'acier, 210 GPa) |
| E2 = 9 000 MPa | 9 GPa | rigidité en tirant **en travers des fibres** : 18 fois moins ! |
| G12 = 6 100 MPa | 6,1 GPa | rigidité en **cisaillement** (quand on fait « glisser » le pli sur lui-même) |
| ν12 = 0,26 | sans unité | coefficient de Poisson : si on tire dans le sens 1, le pli se rétrécit dans le sens 2 de 0,26 fois l'allongement |

Un matériau dont les propriétés dépendent de la direction est dit
**anisotrope**. Le pli est un cas particulier : il a deux directions
privilégiées perpendiculaires (fibres / travers), on dit qu'il est
**orthotrope**.

### 1.2 L'orientation d'un pli

Chaque pli est posé avec ses fibres tournées d'un angle **δ** (delta) par
rapport à l'axe x de la plaque. δ = 0° : fibres selon x ; δ = 90° : fibres
selon y ; δ = 45° : en diagonale.

Pourquoi l'intervalle **]-90°, 90°]** ? Parce qu'une fibre n'a pas de sens :
une fibre à 100° est la même qu'une fibre à -80°. Il y a donc exactement
180 orientations différentes au pas de 1° : -89, -88, …, 0, …, 89, 90.

### 1.3 Le stratifié

Un **stratifié** est un empilement de plis collés. On l'écrit entre crochets
du bas vers le haut : `[0/45/-45/90]` = 4 plis, le premier à 0°, le dernier à
90°. Chez nous : **20 plis**, donc épaisseur totale h = 20 × 0,125 = **2,5 mm**.

**L'idée clé du projet** : en choisissant les angles, on « fabrique » un
matériau sur mesure. Tous les plis à 0° → plaque super rigide selon x, molle
selon y. Des angles bien répartis → plaque qui se comporte pareil dans toutes
les directions. Il y a 180²⁰ ≈ **1,3 × 10⁴⁵** empilements possibles : impossible
de tous les essayer, d'où l'optimisation.

---

## 2. Décrire la rigidité d'un pli : S et Q

*(fichier `laminate.py`, fonctions `ply_compliance` et `ply_stiffness`)*

### 2.1 Loi de Hooke

Pour un ressort : force = raideur × allongement. Pour un matériau, c'est
pareil avec des **contraintes** σ (force par surface, en MPa) et des
**déformations** ε (allongement relatif, sans unité).

Une plaque est fine, donc on ne regarde que ce qui se passe **dans son plan**
(hypothèse des *contraintes planes*). Il y a alors 3 contraintes et 3
déformations :

- σ11, ε11 : traction/allongement selon la direction 1 ;
- σ22, ε22 : selon la direction 2 ;
- σ12, γ12 : cisaillement (γ12 = 2 ε12 est la « distorsion d'angle »).

On les relie par une matrice 3×3.

### 2.2 La souplesse S

Le plus naturel est d'écrire « déformation = S × contrainte », parce que S se
remplit directement avec les constantes de l'énoncé :

```
        |  1/E1     -ν12/E1    0     |
  S  =  | -ν12/E1    1/E2      0     |
        |   0         0       1/G12  |
```

Lecture : si je tire avec σ11, la plaque s'allonge de σ11/E1 selon 1
(1re colonne, 1re ligne) et rétrécit de ν12·σ11/E1 selon 2. Les zéros
disent que tirer ne crée pas de cisaillement (c'est l'orthotropie, dans les
axes du pli).

### 2.3 La rigidité Q

On veut plutôt « contrainte = Q × déformation » : **Q = S⁻¹** (l'inverse de
la matrice). Q est la *matrice de rigidité réduite* du pli. C'est l'objet
central de tout le projet.

### 2.4 Tourner un pli : Q(δ)

*(fonction `rotate_stiffness`)*

Q est écrite dans les axes des fibres. Si le pli est tourné de δ, il faut
exprimer sa rigidité dans les axes x, y de la plaque. Ça donne des formules
en cos⁴δ, sin²δ cos²δ, etc. (la version « cartésienne », slide 27 de P2).
Elles sont lourdes, et c'est justement pour ça que la méthode polaire
(section 4) existe.

---

## 3. Du pli au stratifié : A, B, D

*(fonctions `abd_matrices`, `homogenised_matrices`)*

### 3.1 Membrane et flexion

Une plaque peut être sollicitée de deux façons :

- **en membrane** : on la tire ou on la cisaille dans son plan (comme une
  feuille qu'on étire). Efforts **N**, déformations du plan moyen **ε₀** ;
- **en flexion** : on la plie (comme une règle qu'on courbe). Moments **M**,
  courbures **χ**.

La Théorie Classique des Stratifiés (slide 41) relie tout ça :

```
  N = A ε₀ + B χ
  M = B ε₀ + D χ
```

- **A** : rigidité de **membrane** ;
- **D** : rigidité de **flexion** ;
- **B** : **couplage**. Si B ≠ 0, tirer sur la plaque la fait aussi se
  courber (et inversement). C'est en général gênant : une pièce qui se
  tord quand on la tire, ou qui gauchit en refroidissant après cuisson.

### 3.2 Comment on les calcule

On repère chaque pli k par sa position en hauteur : il occupe
z_{k-1} ≤ z ≤ z_k, avec z = 0 au milieu de la plaque, z = -h/2 en bas et
+h/2 en haut. Puis :

```
  A = Σ Q_k (z_k − z_{k−1})              → épaisseur du pli
  B = ½ Σ Q_k (z_k² − z_{k−1}²)          → position "signée" du pli
  D = ⅓ Σ Q_k (z_k³ − z_{k−1}³)          → position au cube
```

Intuition :

- **A** est une simple **moyenne** des plis : l'ordre n'a pas d'importance.
- **D** pondère par z³ : les plis **à l'extérieur** comptent beaucoup plus
  que ceux du milieu (comme une poutre en I : la matière loin du centre
  travaille le plus en flexion).
- **B** pondère par z², avec un signe : un pli en bas et le même pli en
  haut s'annulent. C'est pour ça qu'un stratifié **symétrique** (miroir par
  rapport au milieu, ex. `[0/45/45/0]`) a toujours B = 0.

### 3.3 Matrices homogénéisées A*, B*, D*, C

A, B et D n'ont pas les mêmes unités (MPa·mm, MPa·mm², MPa·mm³). On les
« normalise » pour les comparer au pli :

```
  A* = A / h      B* = 2B / h²      D* = 12 D / h³      C = A* − D*
```

Toutes sont alors en MPa. Exemple : si tous les plis sont à 0°, A* = D* = Q
et B* = 0. **C = A* − D*** mesure la différence entre le comportement en
membrane et en flexion (C = 0 : la plaque se comporte pareil dans les deux
cas, on dit *homogène*).

---

## 4. La méthode polaire (Verchery, 1979)

*(fichier `polar.py`)*

### 4.1 Le problème des matrices

Une matrice 3×3 comme Q a 6 nombres utiles, mais ces nombres **changent
quand on tourne les axes**. Difficile de répondre à « cette plaque est-elle
isotrope ? » en regardant juste les composantes.

### 4.2 L'idée de Verchery

On réécrit le même tenseur avec 6 autres nombres, mieux choisis
(slides 35-36) :

| Paramètre | Nom | Sens physique |
|---|---|---|
| **T0, T1** | modules isotropes | la partie « identique dans toutes les directions » |
| **R0, R1** | modules anisotropes | **combien** la rigidité varie avec la direction |
| **Φ0, Φ1** | angles polaires | **dans quelle direction** sont les maxima |

Formules (slide 36) :

```
  8 T0             = Q11 − 2 Q12 + 4 Q66 + Q22
  8 T1             = Q11 + 2 Q12 + Q22
  8 R0 e^(4iΦ0)    = Q11 + 4i Q16 − 2 Q12 − 4 Q66 − 4i Q26 + Q22
  8 R1 e^(2iΦ1)    = Q11 + 2i Q16 + 2i Q26 − Q22
```

(on utilise des nombres complexes : R est le module, Φ vient de l'argument).

**Pourquoi c'est génial** :

1. **T0, T1, R0, R1 ne changent pas quand on tourne les axes** (ce sont des
   *invariants*). Tourner les axes de θ revient juste à faire Φ0 → Φ0 − θ et
   Φ1 → Φ1 − θ (slide 37).
2. **Les symétries se lisent directement** (slide 38) :

| Symétrie | Condition polaire | Forme du diagramme polaire |
|---|---|---|
| Orthotropie ordinaire | Φ0 − Φ1 = K·π/4 (K = 0 ou 1) | « os » ou « nœud papillon » |
| **Orthotropie R0** | **R0 = 0** | « cacahuète » (2 lobes) |
| **Symétrie du carré** | **R1 = 0** | « carré arrondi » (4 lobes) |
| Isotropie | R0 = R1 = 0 | cercle parfait |

Le **diagramme polaire** trace la rigidité dans chaque direction θ, sur un
graphique en rond. C'est ce que fait `plots.py`.

### 4.3 Le stratifié en polaire : des sommes de flèches

C'est le résultat le plus important pour comprendre le projet (slides 41-42).
Pour des plis identiques :

- **T0 et T1 de A\* et D\* sont ceux du pli**. On ne peut pas les modifier
  avec les angles : ils ne servent donc à rien dans l'optimisation.
- **B\* et C ont T0 = T1 = 0.**
- Tout ce qu'on contrôle, ce sont les R et les Φ, qui valent :

```
  A* :  R0 e^(4iΦ0) = (1/n)  · R0_pli · Σ_k        e^(4i δ_k)
        R1 e^(2iΦ1) = (1/n)  · R1_pli · Σ_k        e^(2i δ_k)
  B* :  idem avec (1/n²) Σ b_k e^(...)
  D* :  idem avec (1/n³) Σ d_k e^(...)
```

**Image mentale** : chaque pli est une **flèche** de longueur 1 qui pointe
dans la direction 4δ_k (pour R0) ou 2δ_k (pour R1). On additionne les
flèches. Si elles s'annulent, R = 0.

Exemples simples :

- `[0/90]`, pour R1 : flèches à 2×0 = 0° et 2×90 = 180° → elles s'opposent →
  **R1 = 0** en membrane (symétrie du carré). Logique : autant de fibres en x
  qu'en y.
- `[0/45]`, pour R0 : flèches à 0° et 4×45 = 180° → **R0 = 0** en membrane.
- `[0/60/-60]`, pour R0 et R1 : 3 flèches à 120° les unes des autres →
  R0 = R1 = 0 → **isotrope en membrane** (le fameux stratifié « quasi-isotrope »).

Pour B* et D*, chaque flèche est en plus multipliée par un **poids** b_k ou
d_k qui dépend de la position du pli (négatif en bas pour b_k, grand à
l'extérieur pour d_k). C'est pour ça qu'il est beaucoup plus dur d'annuler
plusieurs choses à la fois : les mêmes 20 angles doivent faire s'annuler
plusieurs sommes avec des poids différents.

### 4.4 La norme

Pour mesurer « la taille » d'un tenseur (slide 45) :

```
  ||L|| = √(T0² + 2 T1² + R0² + 4 R1²)
```

Pour notre pli : ||Q|| ≈ 57 000 MPa (pour le T300 du cours, 64 599 MPa).

---

## 5. Ce que doit faire notre plaque (groupe 1)

L'énoncé demande trois symétries, chacune traduite en un **objectif
partiel** Φi (slides 45-47), un nombre ≥ 0 qui vaut **0 quand la symétrie
est parfaitement atteinte** :

| Symétrie demandée | Condition | Objectif partiel | Formule |
|---|---|---|---|
| Découplage | B* = 0 | **Φ1** | (‖B*‖ / ‖Q‖)² |
| Orthotropie R0 en membrane | R0 de A* = 0 | **Φ4** | (R0^A* / R0)² |
| « Orthotropie R1 » en flexion | R1 de D* = 0 | **Φ9** | (R1^D* / R1)² |

On divise par une grandeur du pli pour que chaque Φi soit **sans unité** et
de l'ordre de 1 au pire : on peut alors les additionner.

La **fonction de coût** est la somme (slide 44) :

```
  Φ(δ) = Φ1(δ) + Φ4(δ) + Φ9(δ)        minimum théorique = 0
```

Toute la difficulté : Φ est très **non convexe** en fonction des angles
(des milliers de « creux » locaux), donc les méthodes classiques (descente
de gradient) restent coincées. D'où l'algorithme génétique.

### Deux points que le groupe a tranchés

1. **Φ1 et la slide 51.** Avec la formule du cours, l'exemple de la slide 51
   donne 9,96·10⁻⁸ ; la slide affiche 3,5873·10⁻⁶, exactement **36 = n²**
   fois plus. On garde la formule du cours (option A) et on considère la
   valeur de la slide comme une erreur d'application numérique. À dire dans
   le rapport.
2. **« Orthotropie R1 »** n'existe pas dans le cours : on l'a lue comme
   R1(D*) = 0, que le cours appelle « symétrie du carré » (Φ9). L'autre
   lecture possible serait une coquille pour l'orthotropie R0 (Φ8). À
   confirmer avec le prof ; c'est une ligne dans `config.py`.

### Pièges évités (pour le rapport)

- Quand R0 = 0 ou R1 = 0, l'angle Φ0 ou Φ1 **n'a plus de sens** (une flèche
  de longueur nulle n'a pas de direction). Il ne faut donc jamais combiner
  un objectif sur les angles (Φ3, Φ7) avec un objectif qui annule un R sur
  le même tenseur. `fitness.check_objectives` refuse ces combinaisons. Notre
  groupe n'utilise aucun objectif d'angle, donc pas de problème.
- Φ0 est défini à π/2 près et Φ1 à π près : pour Φ3/Φ7, l'écart Φ0 − Φ1 est
  ramené dans le bon intervalle (`wrap_angle`) avant de le comparer à K·π/4.

---

## 6. L'algorithme génétique (AG)

*(fichier `ga.py`)*

### 6.1 L'idée

On imite Darwin : une **population** de solutions, les meilleures ont plus
d'**enfants**, les enfants **mélangent** les caractères de leurs parents, et
de petites **mutations** apportent de la nouveauté. Au fil des générations,
la population s'améliore.

| Biologie | Notre problème |
|---|---|
| individu | un stratifié (20 angles) |
| gène | un angle de pli |
| génotype (ADN) | les 160 bits qui codent les 20 angles |
| phénotype | les 20 angles en degrés |
| adaptation au milieu | fitness, calculée à partir du coût Φ |

### 6.2 Le codage binaire

Chaque angle est stocké sur **8 bits** (8 chiffres 0/1), parce que :

- 7 bits = 2⁷ = 128 valeurs : pas assez pour 180 angles ;
- 8 bits = 2⁸ = 256 valeurs : assez.

Un individu = 20 × 8 = **160 bits**.

**Le problème des 76 codes en trop** : 256 − 180 = 76 codes ne
correspondent à aucun angle. Deux solutions possibles :

- **modulo** (code % 180) : simple, mais les angles -89° à -14° auraient
  alors 2 codes chacun, donc **2 fois plus de chances** d'apparaître. La
  recherche serait biaisée.
- **rejet** (notre choix) : code 0 → -89°, code 179 → +90°, et les codes
  180-255 sont interdits. La population de départ n'utilise que des codes
  valides, et si un croisement ou une mutation crée un code interdit, ce
  gène est **rejeté** : l'enfant garde le gène de son parent. Chaque angle a
  la même chance. Sur un calcul complet, environ 2 500 gènes sont rejetés
  en 500 générations (colonne `rejected_genes` du CSV).

### 6.3 Les étapes, une par une

```
   population initiale (aléatoire)
            │
            ▼
   ┌──► évaluation : coût Φ de chaque individu
   │        │
   │        ▼
   │    fitness (entre 0 et 1)
   │        │
   │        ▼
   │    sélection (roulette)  → parents
   │        │
   │        ▼
   │    croisement (pc)       → enfants
   │        │
   │        ▼
   │    mutation (pm)
   │        │
   │        ▼
   │    rejet des codes invalides
   │        │
   │        ▼
   │    élitisme : le meilleur parent remplace le pire enfant
   │        │
   └── non ─┴─ génération = Ngen ? ── oui ──► meilleur individu
```

**1. Population initiale.** N = 500 stratifiés tirés au hasard.

**2. Évaluation.** Pour chaque individu : décoder les angles → calculer
A*, B*, D* → paramètres polaires → Φ1 + Φ4 + Φ9.

**3. Fitness** (formule de l'énoncé, p = 1) :

```
  f_i = 1 − (Φ_i − Φ_min) / (Φ_max − Φ_min)
```

Le meilleur de la génération a f = 1, le pire f = 0. Exemple avec trois
individus de coûts 0,01 / 0,05 / 0,11 : fitness 1 / 0,6 / 0.

**4. Sélection par roulette biaisée.** Chaque individu reçoit une part de
roue proportionnelle à sa fitness. On fait tourner la roue 500 fois pour
choisir 500 parents (un bon individu peut être tiré plusieurs fois).
Dans l'exemple : les parts sont 1/1,6 = 62,5 %, 0,6/1,6 = 37,5 % et 0 %.

**5. Croisement** (probabilité pc = 0,85). Les parents vont par deux. On
coupe les deux chaînes de bits au même endroit et on échange les fins :

```
  parent 1 : 10110|010   →   enfant 1 : 10110|111
  parent 2 : 01100|111   →   enfant 2 : 01100|010
```

Dans 15 % des cas, pas de croisement : les enfants sont des copies.

**6. Mutation** (probabilité pm = 1/N par gène, comme dans le cours).
Chaque gène a une petite chance de voir un de ses 8 bits inversé (0 ↔ 1).
Ça évite que toute la population devienne identique et reste coincée.

**7. Élitisme.** Le meilleur individu de la génération précédente remplace
le pire enfant : la meilleure solution trouvée **n'est jamais perdue**.
C'est pour ça que la courbe du meilleur coût ne remonte jamais.

**8. Arrêt** après Ngen = 500 générations.

### 6.4 Les paramètres (dans `config.py`)

| Paramètre | Valeur | Rôle |
|---|---|---|
| N | 500 | taille de la population |
| Ngen | 500 | nombre de générations |
| pc | 0,85 | probabilité de croisement |
| pm | 1/N = 0,002 | probabilité de mutation d'un gène |
| p | 1 | pression de sélection (exposant de la fitness) |
| seed | 1 | graine du hasard : même graine = même résultat |

Ce sont les valeurs de la slide 50 du cours.

---

## 7. Le code, fichier par fichier

| Fichier | Contenu | Parties du cours |
|---|---|---|
| `config.py` | toutes les données : pli, groupe, objectifs, paramètres AG | énoncé §1, P2 slide 50 |
| `laminate.py` | S, Q, Q(δ), A, B, D, A*, B*, D*, C | P2 slides 27, 41 |
| `polar.py` | T0, T1, R0, R1, Φ0, Φ1, norme, sommes polaires directes | P2 slides 35-42, 45 |
| `fitness.py` | les 11 objectifs partiels, le coût Φ, la fitness | P2 slides 44-47, énoncé §2.a |
| `ga.py` | codage, population, roulette, croisement, mutation, rejet, élitisme | P1 slide 48, P2 slide 50 |
| `plots.py` | courbe de convergence, diagrammes polaires | énoncé §3.1.c |
| `main.py` | enchaîne tout et écrit `results/` | — |
| `tests/` | vérifications automatiques | slides 49, 51 |

Chaîne d'appel lors d'un calcul :

```
main.py
 ├─ laminate.ply_compliance → ply_stiffness        (S, Q du pli)
 ├─ ga.run_ga
 │    └─ pour chaque individu : fitness.cost
 │          ├─ laminate.laminate_matrices          (A*, B*, D*, C)
 │          ├─ polar.polar_parameters              (T0, T1, R0, R1, Φ0, Φ1)
 │          └─ fitness.partial_objectives          (Φ1 … Φ11, on garde 1, 4, 9)
 ├─ écriture du CSV et de best_laminate.txt
 └─ plots.plot_convergence / plot_polar_diagrams
```

### Comment on sait que la mécanique est juste

Les tests (`tests/test_mechanics.py`) comparent le code aux valeurs du cours :

- pli T300/5208 (slide 49) : T0 = 26 880, T1 = 24 744, R0 = 19 710,
  R1 = 21 433 MPa → **retrouvés** ;
- stratifié `[9/0/18/-4/14/5]` (slide 51) : tous les paramètres de A*, B*, D*
  **retrouvés à 4 décimales**, Φ0 = Φ1 = 7° ;
- contrôle croisé : la voie cartésienne (matrices) et la voie polaire
  (sommes de flèches) donnent les mêmes nombres sur des empilements au hasard.

Lancer les tests et le calcul (depuis le dossier `Claude Momon's`) :

```bash
../.venv/Scripts/python -m pytest
../.venv/Scripts/python main.py
```

---

## 8. Lire les résultats

Un calcul complet prend environ 35 s. Résultat avec la graine 1 :

```
[22/-41/80/-15/-89/42/-61/61/-74/83/-72/-38/67/-52/43/84/5/38/-25/-82]
Φ = 4,1·10⁻⁵   (Φ1 = 2,5·10⁻⁵, Φ4 = 6,3·10⁻⁶, Φ9 = 9,5·10⁻⁶)
```

Concrètement : R0 de A* = 44 MPa au lieu de 17 700 pour le pli seul (divisé
par 400), R1 de D* = 59 MPa au lieu de 19 000. C'est un très bon
« pseudo-optimum » : pas exactement 0 (impossible avec des angles entiers),
mais très proche.

- **`convergence.*`** : en haut, le meilleur coût (en escalier, il ne
  remonte jamais grâce à l'élitisme), la moyenne et le pire, en échelle
  logarithmique. En bas, l'écart-type : grand au début (population variée),
  petit à la fin (la population s'est regroupée).
- **`polar_diagrams.*`** : la rigidité dans chaque direction. Le pli Q fait
  un « 8 » allongé à 0° (rigide dans le sens des fibres). A* a la forme de
  cacahuète de l'orthotropie R0. D* ressemble à un carré arrondi (symétrie
  du carré). B* est près de 100 fois plus petit que A* (presque découplé ;
  il a sa propre échelle en MPa).
- **`ga_statistics.csv`** : une ligne par génération (min, moyenne, médiane,
  max, écart-type, gènes rejetés, meilleur empilement). S'ouvre directement
  dans Excel.
- **`best_laminate.txt`** : l'empilement, les Φi, tous les paramètres
  polaires et les matrices.

---

## 9. Ce qu'il reste à faire pour le rendu

1. **Confirmer Φ9 ou Φ8** auprès du prof (« orthotropie R1 »).
2. **Plusieurs calculs** avec des graines différentes (`--seed 2`, `3`…) et
   éventuellement le croisement en 2 points (`--crossover two_point`), pour
   montrer dans le rapport que le résultat est robuste.
3. **Le rapport** (énoncé §3) : théorie (sections 2 à 5 de ce document),
   méthodologie (sections 6 et 7, choix du rejet, décision sur Φ1), résultats
   (section 8 et les figures).
4. **Le diagramme de flux** du code (le schéma de la section 6.3 et la
   chaîne d'appel de la section 7 en sont une bonne base).

---

## Glossaire

- **Anisotrope** : propriétés différentes selon la direction.
- **Orthotrope** : anisotrope avec deux directions de symétrie perpendiculaires.
- **Isotrope** : identique dans toutes les directions (comme l'acier).
- **Contraintes planes** : on néglige ce qui se passe dans l'épaisseur.
- **Invariant** : grandeur qui ne change pas quand on tourne les axes.
- **Couplage membrane/flexion** : tirer fait courber (B ≠ 0).
- **Quasi-homogène** : B* = 0 et C = 0 (même comportement partout).
- **Fonction de coût** : nombre à minimiser, ici 0 = objectif atteint.
- **Fitness** : note d'adaptation entre 0 et 1, plus grand = meilleur.
- **Élitisme** : on garde toujours le meilleur individu.
- **Pseudo-optimum** : très bonne solution, pas forcément la meilleure absolue.
