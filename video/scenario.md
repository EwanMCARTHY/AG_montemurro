# Scénario de la vidéo : le projet AG du groupe 1

Vidéo en français, 16:9, 1080p, environ 9 minutes 30. Chaque scène sera une scène Manim (`video/scenes/`) et la narration servira aussi aux sous-titres. Les durées sont estimées à environ 160 mots par minute (débit courant d'une voix off), plus trois ou quatre secondes par scène laissées aux animations. Les durées réelles seront calées sur l'enregistrement de la voix.

Conventions : notation de `docs/explication_du_sujet.tex` (plis numérotés de 1 à n, du bas vers le haut). Valeurs numériques tirées de `config.py` et de `results/best_laminate.txt` (graine 1). Couleurs : un code couleur fixe pour A* (vert), B* (violet), D* (rouge), le pli Q (bleu), comme dans `plots.py`.

| # | Scène | Durée |
|---|---|---|
| 1 | Accroche | 0:30 |
| 2 | Le pli et les deux repères | 1:10 |
| 3 | De S à Q | 0:35 |
| 4 | A, B, D et les matrices étoilées | 1:00 |
| 5 | La méthode polaire | 1:00 |
| 6 | Des flèches qui se referment | 1:10 |
| 7 | Les objectifs du groupe 1 | 0:45 |
| 8 | Deux décisions du groupe | 0:45 |
| 9 | L'algorithme génétique | 1:25 |
| 10 | Résultats | 1:05 |
| 11 | Fin | 0:30 |
| | Total | environ 10:00 (à recaler sur la voix) |

---

## Scène 1 : accroche (0:30)

À l'écran : une plaque vue en coupe, les 20 plis apparaissent un par un, chacun avec des hachures à un angle au hasard. Les angles défilent comme sur un compteur. Puis le calcul s'écrit : $180^{20} \approx 1{,}3\times10^{45}$. Titre : « Optimiser un stratifié par algorithme génétique », sous-titre « EVCSP, groupe 1 ».

Narration :
> Une plaque de vingt couches de fibres de carbone. Pour chaque couche, on choisit une orientation parmi 180. Ça fait 180 puissance 20 empilements possibles, à peu près 10 puissance 45. On ne peut pas tous les essayer. Pourtant, dans ce projet, on en cherche un qui donne à la plaque un comportement bien précis. On va voir ce qu'on cherche, comment on le mesure, et comment un algorithme génétique le trouve.

## Scène 2 : le pli et les deux repères (1:10)

À l'écran : un pli en 3D légère (fibres noires parallèles dans une résine ambrée). Une flèche tire dans le sens des fibres, puis en travers : deux barres comparent $E_1 = 161\,000$ MPa et $E_2 = 9\,000$ MPa, avec un repère « acier : 210 000 MPa ». Les axes 1 (fibres) et 2 (perpendiculaire) apparaissent sur le pli. Puis les axes $x$, $y$ de la plaque, fixes, et le pli tourne d'un angle $\delta$ avec ses axes 1, 2. Trois petits plis montrent $\delta = 0^\circ$, $90^\circ$, $45^\circ$, et trois lignes rappellent : $E_1, E_2, G_{12}, \nu_{12}$ dans les axes du pli ; $\mathbf{A}, \mathbf{B}, \mathbf{D}$ dans les axes de la plaque ; passer de l'un à l'autre = tourner le pli de $\delta$. Ensuite une fibre à $100^\circ$ se superpose à une fibre à $-80^\circ$. L'intervalle $]-90^\circ, 90^\circ]$ s'affiche, avec « 180 valeurs au pas de 1° ».

Narration :
> Commençons par une seule couche, un pli. C'est une feuille de fibres de carbone toutes parallèles, collées par une résine époxyde. Si on tire dans le sens des fibres, le module vaut 161 000 MPa. L'acier, pour comparer, est à 210 000. Si on tire en travers, on tombe à 9 000, dix-huit fois moins. Le pli a deux directions privilégiées, perpendiculaires : on dit qu'il est orthotrope. On les appelle 1, le long des fibres, et 2, en travers.
> Chaque pli est posé avec ses fibres tournées d'un angle delta par rapport à l'axe x de la plaque. Les axes x et y sont fixes ; les axes 1 et 2 tournent avec le pli. Les constantes du pli sont données dans ses axes 1 et 2, les rigidités de la plaque dans les axes x et y : on passe des uns aux autres en tournant le pli de delta.
> Une fibre n'a pas de sens : 100 degrés et moins 80 degrés, c'est la même fibre. Delta va donc de moins 89 à 90 degrés, au pas de 1 degré. Ça fait 180 valeurs.

## Scène 3 : de S à Q (0:35)

À l'écran : la loi de Hooke en contraintes planes, $\{\varepsilon\} = \mathbf{S}\{\sigma\}$, avec la matrice $\mathbf{S}$ remplie de $1/E_1$, $-\nu_{12}/E_1$, $1/E_2$, $1/G_{12}$. Elle se transforme en $\mathbf{Q} = \mathbf{S}^{-1}$ (encadré), avec une ligne qui rappelle le sens des indices : $Q_{11}, Q_{22}$ traction, $Q_{66}$ cisaillement, $Q_{12}$ effet Poisson, $Q_{16} = Q_{26} = 0$ dans les axes du pli. Puis la formule de $\bar Q_{11}(\delta)$ apparaît, suivie de celle de $\bar Q_{16}$, et l'écran se remplit de cosinus et de sinus jusqu'à devenir illisible.

Narration :
> Pour décrire cette rigidité, on écrit la loi de Hooke dans le plan de la plaque : trois déformations, trois contraintes, une matrice 3 par 3. La matrice de souplesse S se remplit directement avec les constantes du pli. On l'inverse, et on obtient Q, la rigidité du pli. Pour un pli tourné de delta, il faut réécrire Q dans les axes de la plaque, et les formules deviennent vite très lourdes. C'est ce que la méthode polaire va simplifier.

## Scène 4 : A, B, D et les matrices étoilées (1:00)

À l'écran : une règle qu'on étire (membrane, efforts $\mathbf{N}$) puis qu'on courbe (flexion, moments $\mathbf{M}$ en flèches courbes), avec « elle s'allonge et reste plate → A » et « elle se courbe → D ». Les deux équations $\mathbf{N} = \mathbf{A}\varepsilon_0 + \mathbf{B}\chi$ et $\mathbf{M} = \mathbf{B}\varepsilon_0 + \mathbf{D}\chi$, avec A, B, D colorés. Une plaque qui se tord quand on la tire illustre $\mathbf{B} \neq 0$, avec la mention « c'est ce que supprimera l'objectif $\Phi_1$ ».
Ensuite la coupe des 20 plis avec l'axe $z$ et le plan moyen. À côté de chaque pli, une barre montre son poids : constant pour A, en $z^3$ pour D (grand à l'extérieur), en $z^2$ avec un signe pour B (négatif en bas, positif en haut). Pour finir, les trois formules $\mathbf{A}^* = \mathbf{A}/h$, $\mathbf{B}^* = 2\mathbf{B}/h^2$, $\mathbf{D}^* = 12\mathbf{D}/h^3$.

Narration :
> On empile maintenant les vingt plis. Une plaque travaille de deux façons : en membrane, quand on la tire dans son plan, et en flexion, quand on la courbe. La théorie classique des stratifiés relie les deux avec trois matrices. A est la rigidité de membrane, D celle de flexion, et B le couplage. Si B n'est pas nul, tirer sur la plaque la fait aussi se courber. C'est ce que l'objectif Phi1 devra supprimer.
> Chaque pli compte selon sa hauteur z dans l'épaisseur. Dans A, tous les plis pèsent pareil. Dans D, le poids va en z au cube, donc les plis de l'extérieur dominent. Dans B, le poids va en z carré avec un signe : un pli en bas et le même pli en haut s'annulent. On divise enfin par l'épaisseur pour obtenir A étoile, B étoile et D étoile, en mégapascals, comparables au pli.

## Scène 5 : la méthode polaire (1:00)

À l'écran : la matrice $\mathbf{Q}$ dont les six composantes changent pendant qu'un repère tourne. Puis les six paramètres polaires apparaissent en deux colonnes : $T_0, T_1$ (modules isotropes), $R_0, R_1$ (modules anisotropes), $\Phi_0, \Phi_1$ (angles polaires). Une ligne précise que $\mathbf{L}$ désigne n'importe laquelle de nos matrices ($\mathbf{Q}$, $\mathbf{A}^*$, $\mathbf{B}^*$, $\mathbf{D}^*$), et une autre fait le lien entre les indices du cours ($L_{1111}$, …) et ceux de Voigt ($L_{11}$, …). Les formules de la slide 36 pour $8T_0$, $8T_1$, $8R_0e^{4i\Phi_0}$, $8R_1e^{2i\Phi_1}$ s'affichent brièvement.
On trace ensuite le diagramme polaire $L_{11}(\theta) = T_0 + 2T_1 + R_0\cos 4(\Phi_0-\theta) + 4R_1\cos 2(\Phi_1-\theta)$ : la courbe démarre sur le « 8 » du pli, puis se déforme pendant que $R_0$ ou $R_1$ glissent vers zéro. On passe par les formes de la slide 38 : cacahuète ($R_0 = 0$), quatre lobes ($R_1 = 0$), cercle ($R_0 = R_1 = 0$).

Narration :
> Le problème de ces matrices, c'est que leurs composantes changent dès qu'on tourne les axes. Difficile de voir si une plaque est isotrope rien qu'en les regardant. En 1979, Verchery propose de réécrire chacune de ces matrices avec six autres nombres. La recette est la même pour Q, A étoile, B étoile ou D étoile : dans les formules, on appelle simplement L la matrice traitée. T0 et T1 sont la partie isotrope, la même dans toutes les directions. R0 et R1 disent de combien la rigidité varie avec la direction. Phi0 et Phi1 sont des angles, qui disent où sont les maxima.
> T0, T1, R0 et R1 ne bougent pas quand on tourne les axes. Et les symétries se lisent directement dessus. Sur le diagramme polaire, qui trace la rigidité dans chaque direction : R0 nul donne une cacahuète, R1 nul donne quatre lobes, et les deux nuls donnent un cercle, une plaque isotrope.

## Scène 6 : des flèches qui se referment (1:10)

À l'écran : les formules de la slide 41 pour $\mathbf{A}^*$ : $T_0^{A^*} = T_0$, $T_1^{A^*} = T_1$, et $R_0^{A^*}e^{4i\Phi_0^{A^*}} = \frac{1}{n}R_0e^{4i\Phi_0}\sum_k e^{4i\delta_k}$ (même chose pour $R_1$ avec $2\delta_k$). La somme $\sum_k e^{4i\delta_k}$ est mise en évidence.
Animation principale dans le plan complexe : chaque pli devient une flèche de longueur 1, orientée à $4\delta_k$. Les flèches se posent bout à bout.
- $[0/45]$ en $4\delta$ : flèches à $0^\circ$ et $180^\circ$, retour au point de départ, $R_0^{A^*} = 0$.
- $[0/60/-60]$ : triangle fermé en $4\delta$ et en $2\delta$, $R_0^{A^*} = R_1^{A^*} = 0$.
Puis les mêmes flèches sont multipliées par les poids $b_k = 2k-n-1$ (pour $\mathbf{B}^*$) et $d_k$ (pour $\mathbf{D}^*$) : leurs longueurs changent, et une somme qui était fermée se rouvre.

Narration :
> Pour un stratifié à plis identiques, le cours donne un résultat simple : les modules isotropes de A étoile et de D étoile sont ceux du pli, quels que soient les angles. Seuls R0 et R1 dépendent de l'empilement, et ils s'écrivent comme des sommes de nombres complexes.
> On peut les voir comme des flèches. Chaque pli est une flèche de longueur 1. Pour R0, elle pointe dans la direction quatre delta ; pour R1, dans la direction deux delta. On met les flèches bout à bout. Si on revient au point de départ, la somme est nulle et R vaut zéro.
> Un pli à 0 et un pli à 45 degrés : pour R0, les flèches pointent à 0 et à 180 degrés, elles s'annulent. Avec 0, 60 et moins 60 degrés, les flèches forment un triangle fermé, pour R0 comme pour R1, et la membrane est isotrope.
> Pour B étoile et D étoile, chaque flèche est en plus multipliée par un poids qui dépend de la place du pli. C'est là toute la difficulté : les mêmes vingt angles doivent refermer plusieurs sommes, chacune avec ses propres poids.

## Scène 7 : les objectifs du groupe 1 (0:50)

À l'écran : la ligne du groupe 1 dans le tableau de l'énoncé (« Découplage, orthotropie R0 en membrane, orthotropie R1 en flexion, 20 plis »). Trois cartes apparaissent, chacune avec sa condition et son objectif partiel :
$\Phi_1 = \left(\|\mathbf{B}^*\| / \|\mathbf{Q}\|\right)^2$, $\Phi_4 = \left(R_0^{A^*}/R_0\right)^2$, $\Phi_9 = \left(R_1^{D^*}/R_1\right)^2$.
Elles se rassemblent dans $\Phi(\boldsymbol\delta) = \Phi_1 + \Phi_4 + \Phi_9$, $\min \Phi = 0$. Pour finir, une coupe 1D de $\Phi$ en faisant varier un seul angle (calculée avec `fitness.cost`), pleine de creux, avec une bille qui tombe dans le premier creux venu.

Narration :
> Notre groupe doit obtenir trois propriétés. Le découplage, c'est-à-dire B étoile nul. L'orthotropie R0 en membrane : R0 de A étoile nul. Et en flexion, R1 de D étoile nul. Chaque condition devient un objectif partiel, un nombre positif qui vaut zéro quand la propriété est atteinte. On divise chaque fois par une grandeur du pli, pour que les trois soient sans unité et qu'on puisse les additionner. La fonction de coût est leur somme, et son minimum vaut zéro.
> Le piège, c'est la forme de cette fonction quand on fait varier les angles : elle a énormément de creux locaux. Une méthode de gradient s'arrêterait dans le premier venu. D'où l'algorithme génétique.

## Scène 8 : deux décisions du groupe (0:45)

À l'écran : deux encadrés orange, l'un après l'autre.
1. Slide 51, $[9/0/18/-4/14/5]$ : « notre formule : $9{,}96\times10^{-8}$ », « slide : $3{,}5873\times10^{-6}$ », puis « rapport = 36 = $n^2$ ». Conclusion affichée : « on garde la formule de la slide 45 ».
2. « Orthotropie $R_1$ » barré d'un point d'interrogation, flèche vers « $R_1^{D^*} = 0$, symétrie du carré, $\Phi_9$ », avec la mention « à confirmer avec le professeur ».

Narration :
> Deux points de l'énoncé nous ont obligés à trancher. Le premier concerne Phi1. Sur l'exemple de la slide 51, notre formule donne environ 10 puissance moins 7. La slide affiche une valeur exactement 36 fois plus grande, et 36, c'est le nombre de plis au carré. On garde la formule de la slide 45 et on considère la valeur de la slide comme une erreur numérique.
> Le second : l'énoncé parle d'orthotropie R1 en flexion, un terme qui n'existe pas dans le cours. On l'a lu comme R1 de D étoile nul, ce que le cours appelle la symétrie du carré. On attend la confirmation du professeur ; si on s'est trompés, c'est une ligne à changer dans le code.

## Scène 9 : l'algorithme génétique (1:40)

À l'écran, en quatre temps.
1. Correspondance biologie / problème : individu = stratifié, gène = angle, génotype = 160 bits.
2. Codage : un angle, ses 8 bits, $2^7 = 128 < 180 \le 256 = 2^8$. Une bande de 256 codes, dont 180 en vert (valides) et 76 en gris. Comparaison : en modulo, 76 angles reçoivent deux codes (histogramme déséquilibré) ; avec le rejet, l'histogramme est plat. Formule $\delta = -89^\circ + \text{code}$.
3. La boucle (schéma de la section 6.3 du document), parcourue étape par étape avec une mini-animation pour chacune :
   - fitness : trois individus de coûts 0,01 ; 0,05 ; 0,11 qui reçoivent 1 ; 0,6 ; 0 ;
   - roulette : une roue avec des parts de 62,5 % et 37,5 % qui tourne ;
   - croisement : `10110|010` et `01100|111` échangent leurs fins ;
   - mutation : un bit qui clignote et s'inverse ;
   - élitisme : le meilleur parent prend la place du pire enfant.
4. Les paramètres : $N = 500$, $N_{gen} = 500$, $p_c = 0{,}85$, $p_m = 1/N$, $p = 1$.

Narration :
> Un algorithme génétique imite l'évolution. Chaque individu est un stratifié, chaque gène est un angle de pli.
> Chaque angle est codé sur 8 bits. Sept bits ne donnent que 128 valeurs, pas assez pour 180 angles ; huit en donnent 256. Il reste donc 76 codes qui ne correspondent à aucun angle. Avec un modulo, 76 angles auraient eu deux codes et seraient sortis deux fois plus souvent. On a choisi le rejet : si un enfant reçoit un code interdit, il garde le gène de son parent.
> La boucle part de 500 stratifiés tirés au hasard. On calcule le coût de chacun, puis sa fitness : 1 pour le meilleur, 0 pour le pire. À la sélection, chaque individu reçoit une part de roulette proportionnelle à sa fitness, et on tourne la roue 500 fois pour choisir les parents. Les parents vont par deux : dans 85 % des cas, on coupe leurs bits au même endroit et on échange les fins. Puis la mutation : chaque gène a une chance sur 500 de voir un de ses bits inversé, ce qui garde de la diversité. Enfin, le meilleur individu de la génération précédente remplace le pire enfant. On ne perd donc jamais la meilleure solution. Et on recommence, 500 fois.

## Scène 10 : résultats (1:05)

À l'écran :
1. La courbe de convergence se trace génération par génération (données de `ga_statistics.csv`, échelle log) : meilleur coût en escalier, moyenne, pire.
2. En parallèle, un nuage de 500 points (un par individu, coût en ordonnée) qui se resserre au fil des générations. Les données viennent d'une copie de la boucle de `ga.py` dans `video/`, qui enregistre la population entière (le code du projet n'est pas modifié).
3. Le meilleur empilement s'affiche : $[22/-41/80/-15/-89/42/-61/61/-74/83/-72/-38/67/-52/43/84/5/38/-25/-82]$, $\Phi = 4{,}1\times10^{-5}$.
4. Les 20 flèches de ce stratifié pour $R_0^{A^*}$ se posent bout à bout et se referment presque.
5. Le diagramme polaire part du « 8 » du pli et se déforme vers $\mathbf{A}^*$ (allongé à 90°), puis vers $\mathbf{D}^*$ (presque rond). $\mathbf{B}^*$ apparaît à part, avec son échelle en MPa.

Narration :
> Voici un calcul complet, avec la graine 1. Il tourne en 35 secondes environ. Le meilleur coût descend par paliers et ne remonte jamais, grâce à l'élitisme. Au début, la population est très dispersée ; à la fin, elle s'est resserrée autour des meilleures solutions.
> Le meilleur stratifié a un coût de 4 fois 10 puissance moins 5. R0 de A étoile vaut 44 MPa, contre 17 700 pour le pli seul : 400 fois moins. R1 de D étoile vaut 59 MPa au lieu de 19 000.
> Sur les diagrammes polaires, le pli seul fait un huit allongé dans le sens des fibres. A étoile n'a plus que ses deux lobes : c'est l'orthotropie R0. D étoile est presque rond, avec quatre bosses très légères. Et B étoile est si petit qu'il lui faut sa propre échelle, quelques centaines de MPa contre près de 85 000 pour A étoile. Avec des angles entiers, on ne tombe pas pile sur zéro, mais on en est très près.

## Scène 11 : fin (0:30)

À l'écran : le chemin complet en une ligne de schémas (pli, matrices étoilées, flèches, boucle de l'AG, diagrammes polaires), puis une liste « reste à faire » : confirmer $\Phi_9$, relancer avec d'autres graines, rédiger le rapport. Dernier plan : nom du dépôt `EwanMCARTHY/AG_montemurro`, « EVCSP, groupe 1 ».

Narration :
> On part donc des constantes d'un pli, on construit A étoile, B étoile et D étoile, la méthode polaire transforme les symétries voulues en flèches qui doivent se refermer, et l'algorithme génétique cherche les vingt angles qui les referment. Il nous reste à confirmer Phi9 avec le professeur, à relancer le calcul avec d'autres graines pour vérifier que le résultat tient, et à écrire le rapport.

---

## Points à valider

1. Scène 10 : décrire $\mathbf{D}^*$ comme « presque rond, avec quatre bosses très légères » plutôt que « carré arrondi ». Sur la figure, $R_1^{D^*} \approx 59$ MPa mais $R_0^{D^*} \approx 1\,410$ MPa reste faible devant $T_0 + 2T_1 \approx 67\,600$ MPa, donc la forme est très proche d'un cercle.
2. Scène 10 : $\|\mathbf{B}^*\|$ vaut environ 1/140 de $\|\mathbf{A}^*\|$. J'ai préféré donner les ordres de grandeur affichés sur les diagrammes (quelques centaines de MPa contre environ 85 GPa au maximum pour $A^*_{11}$) plutôt que « cent fois plus petit ».
3. Scène 10 : le nuage de population demande de relancer l'AG dans une copie de la boucle qui enregistre les 500 coûts à chaque génération. Même graine, même résultat attendu ; je vérifierai que le meilleur empilement est identique.
