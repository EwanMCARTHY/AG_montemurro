# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 00:26:30 2024

@author: nicol
"""
# Importation des modules nécessaires
from gen_benchmark import Population, Individu  # Import des classes pour l'algorithme génétique
import benchmark as b  # Module contenant les fonctions de benchmark comme  rastrigin
import numpy as np  # Bibliothèque pour les calculs numériques
import matplotlib.pyplot as plt  # Bibliothèque pour la visualisation

# Paramètres pour la fonction Ackley
# Définir les dimensions et les limites de recherche
taille_population = 600  # Taille de la population
nombre_genes = 2  # Nombre de variables (dimensions) dans la fonction
valeur_min = -5.12  # Borne inférieure des gènes
valeur_max = 5.12 # Borne supérieure des gènes
probabilite_croisement = 0.85  # Probabilité de croisement
probabilite_mutation = 1 / taille_population  # Probabilité de mutation (inversement proportionnelle à la taille de la population)
nombre_generations = 500  # Nombre total de générations
nombre_executions = 100  # Nombre de fois que l'algorithme est exécuté

# Listes pour stocker les statistiques des exécutions
meilleures_solutions = []  # Liste des meilleures solutions pour chaque exécution
pire_solutions = []  # Liste des pires pondérations par exécution
moyennes_par_execution = []  # Moyennes des pondérations par exécution
variances_par_execution = []  # Variances des pondérations par exécution
courbes_meilleures_solutions = []  # Courbes de l'évolution du meilleur individu pour chaque exécution

# Fonction pour une exécution unique de l'algorithme génétique
def executer_AG():
    """
    Exécute une itération complète de l'algorithme génétique avec la fonction Ackley.
    Retourne :
    - La pondération du meilleur individu trouvé.
    - La courbe de l'évolution des pondérations du meilleur individu à chaque génération.
    """
    # Initialisation de la population
    population = Population(
        taille_popu=taille_population,
        n_gènes=nombre_genes,
        val_min=valeur_min,
        val_max=valeur_max,
        p_cross=probabilite_croisement,
        p_mut=probabilite_mutation,
        fonction_objectif=b.rastrigin  # Utilisation de la fonction Ackley comme fonction objectif
    )
    courbe_best_individu = []  # Liste pour stocker les pondérations du meilleur individu à chaque génération

    # Boucle principale sur les générations
    for generation in range(nombre_generations):
        # Mise à jour des fitness pour la population actuelle
        population.mise_a_jour_fitness()
        
        # Trouver le meilleur individu de la génération
        meilleur = population.meilleur_individu()
        courbe_best_individu.append(meilleur.pondération)  # Ajouter sa pondération à la courbe
        
        # Étapes de l'algorithme génétique
        couples = population.sélection_couples()  # Sélection biaisée des couples
        enfants = population.croisement(couples)  # Croisement des couples pour générer des enfants
        population.mutation(enfants)  # Appliquer la mutation sur les enfants
        population.individus = enfants  # Mise à jour de la population avec les enfants
        population.élitisme()  # Élitisme : conserver le meilleur individu précédent

    # Retourner la meilleure pondération finale et la courbe d'évolution
    meilleur_final = population.meilleur_individu()
    return meilleur_final.pondération, courbe_best_individu

# Exécutions multiples pour générer des statistiques globales
for execution in range(nombre_executions):
    print(f"\n--- Exécution {execution + 1} ---")
    # Exécuter l'algorithme génétique une fois
    meilleur, courbe = executer_AG()
    
    # Stocker les résultats de l'exécution
    meilleures_solutions.append(meilleur)  # Meilleure solution trouvée
    courbes_meilleures_solutions.append(courbe)  # Courbe de la meilleure solution
    pire_solutions.append(max(courbe))  # Pire pondération observée
    moyennes_par_execution.append(np.mean(courbe))  # Moyenne des pondérations
    variances_par_execution.append(np.var(courbe))  # Variance des pondérations

# Analyse des résultats globaux
meilleure_solution_globale = min(meilleures_solutions)  # Meilleure pondération trouvée parmi toutes les exécutions
pire_solution_globale = max(meilleures_solutions)  # Pire pondération trouvée parmi toutes les exécutions
moyenne_globale = np.mean(meilleures_solutions)  # Moyenne des meilleures solutions
variance_globale = np.var(meilleures_solutions)  # Variance des meilleures solutions

# Identifier la courbe correspondant à la meilleure solution globale
index_meilleure_execution = meilleures_solutions.index(meilleure_solution_globale)
courbe_meilleure_execution = courbes_meilleures_solutions[index_meilleure_execution]

# Affichage des statistiques globales
print("\n--- Statistiques globales ---")
print("Fonction d'évaluation : Rastrigin")
print(f"Meilleure solution globale : {meilleure_solution_globale:.4f}")
print(f"Exécution de la meilleure solution globale : {index_meilleure_execution + 1}")
print(f"Pire solution globale : {pire_solution_globale:.4f}")
print(f"Moyenne des meilleures solutions : {moyenne_globale:.4f}")
print(f"Variance des meilleures solutions : {variance_globale:.4f}")

# Tracé de la courbe d'évolution pour la meilleure exécution
plt.figure(figsize=(10, 6))
plt.plot(courbe_meilleure_execution, label="Meilleure Exécution")
plt.xlabel("Générations")
plt.ylabel("Pondération du Meilleur Individu")
plt.title("Évolution de la Pondération du Meilleur Individu avec Rastrigin")
plt.legend()
plt.grid()
plt.show()


"""

--- Statistiques globales ---
Fonction d'évalutation : Rastrigin
Meilleure solution globale : 2.3098
Exécution de la meilleure solution globales :85.0000
Pire solution globale : 12.3661
Moyenne des meilleures solutions : 6.4062
Variance des meilleures solutions : 4.0248
"""