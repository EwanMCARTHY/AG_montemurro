# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 00:35:22 2024

@author: nicol
"""

from gen_benchmark import Population
from gen_benchmark import Individu
import benchmark as b
import numpy as np
import matplotlib.pyplot as plt

#cas pour Holder table

# Paramètres de l'algorithme génétique
taille_population = 600
nombre_genes = 2
valeur_min = -10 #simulation infini
valeur_max = 10 # inifini
probabilite_croisement = 0.85
probabilite_mutation = 1 / taille_population
nombre_generations = 500
nombre_executions = 100

# Listes pour stocker les statistiques
meilleures_solutions = []
pire_solutions = []
moyennes_par_execution = []
variances_par_execution = []
courbes_meilleures_solutions = []

# Fonction pour exécuter une simulation unique
def executer_AG():
    population = Population(
        taille_popu=taille_population,
        n_gènes=nombre_genes,
        val_min=valeur_min,
        val_max=valeur_max,
        p_cross=probabilite_croisement,
        p_mut=probabilite_mutation,
        fonction_objectif=b.holder_table ## choix de la fonction
    )
    
    courbe_best_individu = []
    
    for generation in range(nombre_generations):
        population.mise_a_jour_fitness()
        meilleur = population.meilleur_individu()
        courbe_best_individu.append(meilleur.pondération)
        
        couples = population.sélection_couples()
        enfants = population.croisement(couples)
        population.mutation(enfants)
        population.individus = enfants
        population.élitisme()
    
    meilleur_final = population.meilleur_individu()
    return meilleur_final.pondération, courbe_best_individu

# Exécutions multiples
for execution in range(nombre_executions):
    print(f"\n--- Exécution {execution + 1} ---")
    meilleur, courbe = executer_AG()
    meilleures_solutions.append(meilleur)
    courbes_meilleures_solutions.append(courbe)
    pire_solutions.append(max(courbe))
    moyennes_par_execution.append(np.mean(courbe))
    variances_par_execution.append(np.var(courbe))

# Analyse des résultats
meilleure_solution_globale = min(meilleures_solutions)
pire_solution_globale = max(meilleures_solutions)
moyenne_globale = np.mean(meilleures_solutions)
variance_globale = np.var(meilleures_solutions)

meilleure_solution_globale = min(meilleures_solutions)
pire_solution_globale = max(meilleures_solutions)
moyenne_globale = np.mean(meilleures_solutions)
variance_globale = np.var(meilleures_solutions)
# Courbe de la meilleure exécution
index_meilleure_execution = meilleures_solutions.index(meilleure_solution_globale)
courbe_meilleure_execution = courbes_meilleures_solutions[index_meilleure_execution]

# Affichage des statistiques
print("\n--- Statistiques globales ---")
print("Fonction d'évalutation : Holder Table")
print(f"Meilleure solution globale : {meilleure_solution_globale:.4f}")
print(f"Exécution de la meilleure solution globales :{index_meilleure_execution :.4f}")
print(f"Pire solution globale : {pire_solution_globale:.4f}")
print(f"Moyenne des meilleures solutions : {moyenne_globale:.4f}")
print(f"Variance des meilleures solutions : {variance_globale:.4f}")

# Tracé de la courbe d'évolution
plt.figure(figsize=(10, 6))
plt.plot(courbe_meilleure_execution, label="Meilleure Exécution")
plt.xlabel("Générations")
plt.ylabel("Pondération du Meilleur Individu")
plt.title("Évolution de la Pondération du Meilleur Individu avec Holder Table")
plt.legend()
plt.grid()
plt.show()

"""
--- Statistiques globales ---
Fonction d'évalutation : Holder Table
Meilleure solution globale : -19.2084
Exécution de la meilleure solution globales :54.0000
Pire solution globale : -18.4460
Moyenne des meilleures solutions : -19.1233
Variance des meilleures solutions : 0.0147
"""