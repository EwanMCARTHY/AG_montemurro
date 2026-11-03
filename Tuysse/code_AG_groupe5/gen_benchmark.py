# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 22:12:20 2024

@author: nicol
"""

import random as rd


class Individu:
    def __init__(self, gènes, fonction_objectif):
        """
        Initialise un individu avec des gènes et une fonction objectif.
        :param gènes: Liste des gènes représentant l'individu.
        :param fonction_objectif: Fonction pour évaluer la pondération de l'individu.
        """
        self.gènes = gènes
        self.fonction_objectif = fonction_objectif
        self.pondération = self.fonction_objectif(gènes)  # Calcul initial de la pondération
        self.fitness = 0  # Valeur normalisée pour la sélection

    def calcul_fitness(self, phi_min, phi_max):
        """
        Met à jour la fitness à partir de la pondération.
        :param phi_min: Meilleure pondération de la population.
        :param phi_max: Pire pondération de la population.
        """
        if phi_max != phi_min:
            self.fitness = 1 - (self.pondération - phi_min) / (phi_max - phi_min)
        else:
            self.fitness = 1

    def muter(self, val_min, val_max, p_mut):
        """
        Applique une mutation aléatoire à chaque gène avec probabilité p_mut.
        :param val_min: Valeur minimale possible pour un gène.
        :param val_max: Valeur maximale possible pour un gène.
        :param p_mut: Probabilité de mutation.
        """
        self.gènes = [
            rd.uniform(val_min, val_max) if rd.random() < p_mut else g
            for g in self.gènes
        ]
        self.pondération = self.fonction_objectif(self.gènes)  # Recalcul après mutation

    def __repr__(self):
        """
        Représentation lisible de l'individu.
        """
        return f"Individu(gènes={self.gènes}, pondération={self.pondération:.4f}, fitness={self.fitness:.4f})"



class Population:
    def __init__(self, taille_popu, n_gènes, val_min, val_max, p_cross, p_mut, fonction_objectif):
        """
        Initialise la population.
        """
        self.taille_popu = taille_popu
        self.n_gènes = n_gènes
        self.val_min = val_min
        self.val_max = val_max
        self.p_cross = p_cross
        self.p_mut = p_mut
        self.fonction_objectif = fonction_objectif

        # Initialisation des individus
        self.individus = [
            Individu(
                [rd.uniform(val_min, val_max) for _ in range(n_gènes)],
                self.fonction_objectif
            )
            for _ in range(taille_popu)
        ]
        self.mise_a_jour_fitness()

    def mise_a_jour_fitness(self):
        """Met à jour la pondération et la fitness de chaque individu."""
        for individu in self.individus:
            individu.pondération = self.fonction_objectif(individu.gènes)
        phi_min = min(ind.pondération for ind in self.individus)
        phi_max = max(ind.pondération for ind in self.individus)
        for individu in self.individus:
            individu.calcul_fitness(phi_min, phi_max)

    def meilleur_individu(self):
        """Retourne l'individu avec la meilleure pondération."""
        return min(self.individus, key=lambda ind: ind.pondération)

    def pire_individu(self):
        """Retourne l'individu avec la pire pondération."""
        return max(self.individus, key=lambda ind: ind.pondération)

    def sélection_couples(self):
        """Sélectionne des couples pour la reproduction basée sur une loterie biaisée."""
        total_fitness = sum(ind.fitness for ind in self.individus)
        probabilités = [ind.fitness / total_fitness for ind in self.individus]
        couples = []
        for _ in range(self.taille_popu // 2):
            parent1 = rd.choices(self.individus, weights=probabilités, k=1)[0]
            parent2 = rd.choices(self.individus, weights=probabilités, k=1)[0]
            couples.append((parent1, parent2))
        return couples

    def croisement(self, couples):
        """
        Crée de nouveaux individus à partir des couples avec croisement en un point basé sur p_cross.
        :param couples: Liste des couples sélectionnés.
        """
        enfants = []
        for parent1, parent2 in couples:
            if rd.random() < self.p_cross:  # Applique le croisement avec une probabilité p_cross
                point_croisement = rd.randint(1, self.n_gènes - 1)
                gènes_enfant1 = parent1.gènes[:point_croisement] + parent2.gènes[point_croisement:]
                gènes_enfant2 = parent2.gènes[:point_croisement] + parent1.gènes[point_croisement:]
            else:
            # Pas de croisement, les enfants sont des clones des parents
                gènes_enfant1 = parent1.gènes[:]
                gènes_enfant2 = parent2.gènes[:]
        
        # Créer les enfants avec la fonction objectif
                enfants.append(Individu(gènes_enfant1, self.fonction_objectif))
                enfants.append(Individu(gènes_enfant2, self.fonction_objectif))
        return enfants

    def mutation(self, enfants):
        """Applique des mutations aléatoires aux enfants."""
        for enfant in enfants:
            enfant.muter(self.val_min, self.val_max, self.p_mut)
        return enfants

    def nouvelle_génération(self):
        """Crée une nouvelle génération."""
        couples = self.sélection_couples()
        enfants = self.croisement(couples)
        enfants_mutés = self.mutation(enfants)
        self.individus = enfants_mutés
        self.mise_a_jour_fitness()

    def élitisme(self):
        """Remplace le pire individu de la nouvelle génération par le meilleur individu de l'ancienne."""
        meilleure_ancienne = self.meilleur_individu()
        pire_nouvelle = self.pire_individu()
        self.individus.remove(pire_nouvelle)
        self.individus.append(meilleure_ancienne)
        self.mise_a_jour_fitness()

    def __repr__(self):
        """Représentation lisible de la population."""
        return f"Population:\n" + "\n".join([str(ind) for ind in self.individus])
