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
nombre_genes = 10
"""
valeur_min = -1e100 #simulation infini
valeur_max = 1e100 # inifini
"""
valeur_min = -10 
valeur_max = 10
probabilite_croisement = 0.85
probabilite_mutation = 1 / taille_population
nombre_generations = 400
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
        fonction_objectif=b.sphere ## choix de la fonction
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

# Courbe de la meilleure exécution
index_meilleure_execution = meilleures_solutions.index(meilleure_solution_globale)
courbe_meilleure_execution = courbes_meilleures_solutions[index_meilleure_execution]

# Affichage des statistiques
print("\n--- Statistiques globales ---")
print("Fonction d'évalutation : Sphere")
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
plt.title("Évolution de la Pondération du Meilleur Individu avec sphere")
plt.legend()
plt.grid()
plt.show()

"""
--- Statistiques globales ---

Meilleure solution globale : 63877589977644003740242507997895292460914831852618150231637769649754459235143324049506601496745624268267629119651542138822472810509227856655947768850493192787230380491177729958984652689003792826368.0000
Pire solution globale : 1976675457225143529626698779961799357787375393295353009504338481081761145588753963830299010301452847628857845716090361427017487685759588991780513252962770322337405287446770457284268655643053122387968.0000
Moyenne des meilleures solutions : 454097337544850635960160640392556965462589788229930242348402229753545425496511767093158646987495135936519608565361061013700285886232201516497993586830749364374578425862165786374708423320474147094528.0000
Variance des meilleures solutions : inf
"""

"""
--- Statistiques globales ---
Fonction d'évalutation : Sphere
Meilleure solution globale : 0.0582
Exécution de la meilleure solution globales :32.0000
Pire solution globale : 2.3174
Moyenne des meilleures solutions : 0.7055
Variance des meilleures solutions : 0.2195
"""
