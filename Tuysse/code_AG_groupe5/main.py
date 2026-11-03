# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 20:02:56 2024

@author: nicol
"""
from gen import Population
from gen import Individu
import fitness as ft


# Importation des modules nécessaires
import random as rd
import numpy as np
import matplotlib.pyplot as plt

# Paramètres de l'algorithme
taille_popu = 300        # Nombre d'individus dans la population
n_gènes = 24              # Nombre de gènes par individu
val_min = -89           # Valeur minimale des gènes
val_max = 90             # Valeur maximale des gènes
p_cross = 0.7             # Probabilité de croisement
p_mut = 1/taille_popu             # Probabilité de mutation
n_generations = 100        # Nombre de générations à simuler

# Initialisation de la population
population = Population(taille_popu, n_gènes, val_min, val_max, p_cross, p_mut, mêmes_propriétés=True)

 # Récupération du pire individu de la population

# Liste pour stocker les meilleurs individus de chaque génération
meilleurs_individus = []

# Boucle principale de l'algorithme génétique
for generation in range(n_generations): # Exécution sur le nombre de générations défini
    print(f"\n--- Génération {generation + 1} ---") # Affichage du numéro de la génération en cours
    
    # Actualisation des fitness
    population.actualisation_fitness()
    
    # Meilleur individu de la génération
    meilleur = population.meilleur_individu()
    print(f"Meilleur individu : {meilleur}")
    meilleurs_individus.append(meilleur)
    
    # Étapes de l'algorithme génétique
    couples = population.sélection_couples()  # Sélection biaisée des couples
    enfants = population.croisement(couples)  # Croisement avec cross-over
    population.mutation(enfants)  # Mutation aléatoire des enfants
    enfants = population.élitisme(enfants)  # Élitisme pour conserver le meilleur individu précédent
    population.nouvelle_génération(enfants)  # Remplacement de la population



# Affichage des résultats finaux
# Création des listes pour les valeurs de fitness du meilleur individu de chaque génération
Y=[meilleurs_individus[i].pondération for i in range(len(meilleurs_individus))] 
X=[i for i in range(len(meilleurs_individus))]
plt.plot(X, Y)
plt.xlabel("générations")
plt.ylabel("valeur de phi")
plt.grid()

plt.show()

