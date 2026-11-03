# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 13:29:26 2024

@author: nicol
"""

import random as rd
import fitness as ft
import numpy as np

class Individu: # Stratifié composite sous forme d'un individu dans un algorithme génétique
    def __init__(self, gènes, E1, E2, nu12, G12, e_pli):
        self.gènes = gènes  # Liste des gènes de l'individu
        self.pondération = 0
        self.fitness = 0  # Valeur de la fitness
        
        # Propriétés mécaniques distinctes
        self.E1 = E1
        self.E2 = E2
        self.nu12 = nu12
        self.G12 = G12
        self.e_pli = e_pli
        self.n_pli = len(self.gènes)
        
        self.h = self.e_pli * len(self.gènes) # Hauteur totale du stratifié
        
        #Calcul de la matrice de rigidité de base
        self.Q=ft.Q(E1, E2, nu12, G12)
        
        # Calcul de la matrice Q de référence pour les paramètres polaires de base
        self.Q_V= ft.Voigt(ft.Q(E1, E2, nu12, G12))
        
        # Calcul des différences matrices Q dans le repère global
        self.matrices_Q = [np.dot (ft.inv_rotation(theta),self.Q_V) for theta in self.gènes]
        
        # Calcul des hauteurs intermédiaires entre plis
        self.Z =ft.Z(self.n_pli, self.e_pli)  
        
        
        # Calcul des différents tenseurs de rigidité
        self.A = ft.A(self.matrices_Q,self.n_pli,self.e_pli)
        self.B = ft.B(self.e_pli, self.matrices_Q,self.Z)
        self.D = ft.D(self.e_pli, self.matrices_Q, self.Z)
        
    
        #Définition des différents tenseurs normalisés utiles pour l'étude
        self.As = 1 / self.h * self.A
        self.Bs = 2 / self.h**2 * self.B
        self.Ds = 12 / self.h**3 * self.D

        
        self.C = self.As - self.Ds

        # Calculs des fonctions d'objectif
        self.phi_1 = ft.phi_1(self.B, self.h, self.Q_V)      
        self.phi_2 = ft.phi_2(self.C, self.Q_V)
        self.phi_6 = ft. phi_6(self.A, self.h,self.Q_V)
            
        # Calcul initial de la pondération
        self.pondération = ft.phi_tot(self.As, self.Bs, self.C, self.h, self.Q_V)
        
        # Calcul initial de la fitness (sera mis à jour dynamiquement)
        self.fitness = 0
    
    def calcul_fitness(self, phi_min, phi_max):
        """Met à jour la fitness à partir de la pondération."""
        if phi_max != phi_min:  # Évite la division par zéro
            self.fitness = 1 - (self.pondération - phi_min) / (phi_max - phi_min)
        else:
            self.fitness = 1
    
    def muter(self, val_min, val_max, p_mut):
        """Applique une mutation aléatoire à chaque gène avec probabilité p_mut."""
        self.gènes = [
            rd.randint(val_min, val_max) if rd.random() < p_mut else g
            for g in self.gènes
        ]
    
    def __repr__(self):
        """Représentation lisible de l'individu (sans les propriétés mécaniques)."""
        return f"Individu(gènes={self.gènes}, pondération={self.pondération}, fitness={self.fitness})"




class Population:
    def __init__(self, taille_popu, n_gènes, val_min, val_max, p_cross, p_mut, mêmes_propriétés=False):
        self.taille_popu = taille_popu
        self.n_gènes = n_gènes
        self.val_min = val_min
        self.val_max = val_max
        self.p_cross = p_cross
        self.p_mut = p_mut
        self.mêmes_propriétés = mêmes_propriétés

        # Initialisation des propriétés mécaniques (optionnelles)
        if mêmes_propriétés:
            self.E1 = 161000
            self.E2 = 9000
            self.nu12 = 0.26
            self.G12 = 6100
            self.e_pli = 0.125E-3
        else:
            self.E1 = self.E2 = self.nu12 = self.G12 = self.e_pli = None

        # Initialisation des individus
        self.individus = [
            Individu(
                [rd.randint(val_min, val_max) for _ in range(n_gènes)],
                E1=self.E1,
                E2=self.E2,
                nu12=self.nu12,
                G12=self.G12,
                e_pli=self.e_pli
            )
            for _ in range(taille_popu)
        ]

    # --- Algorithme génétique ---

    def actualisation_fitness(self): 
        """Met à jour la fitness de tous les individus."""
        phi_min = min(ind.pondération for ind in self.individus)
        phi_max = max(ind.pondération for ind in self.individus)
        for individu in self.individus:
            individu.calcul_fitness(phi_min, phi_max)

    def meilleur_individu(self):
        """Retourne l'individu avec la meilleure pondération."""
        return min(self.individus, key=lambda ind: ind.pondération)

    def pire_individu(self):
        """Retourne l'individu avec la plus faible pondération."""
        return max(self.individus, key=lambda ind: ind.pondération)

    def sélection_couples(self):
        """Sélection des couples biaisée pondérée sur fitness."""
        total_fitness = sum(ind.fitness for ind in self.individus)
        probabilités = [ind.fitness / total_fitness for ind in self.individus]
        couples = []
        for _ in range(self.taille_popu // 2):
            parent1 = rd.choices(self.individus, weights=probabilités, k=1)[0]
            parent2 = rd.choices(self.individus, weights=probabilités, k=1)[0]
            couples.append((parent1, parent2))
        return couples

    def croisement(self, couples):
        """Crée de nouveaux individus à partir des couples avec croisement en un point basé sur p_cross."""
        enfants = []
        for parent1, parent2 in couples:
            if rd.random() < self.p_cross:  # Applique le croisement uniquement avec une probabilité p_cross
                point_croisement = rd.randint(1, self.n_gènes - 1)
                gènes_enfant1 = parent1.gènes[:point_croisement] + parent2.gènes[point_croisement:]
                gènes_enfant2 = parent2.gènes[:point_croisement] + parent1.gènes[point_croisement:]
            else:
            # Pas de croisement : les enfants sont des copies exactes des parents
                gènes_enfant1 = parent1.gènes[:]
                gènes_enfant2 = parent2.gènes[:]
        
        # Créer les individus enfants
            enfants.append(
                Individu(gènes_enfant1, parent1.E1, parent1.E2, parent1.nu12, parent1.G12, parent1.e_pli)
                )   
            enfants.append(
                Individu(gènes_enfant2, parent2.E1, parent2.E2, parent2.nu12, parent2.G12, parent2.e_pli)
                )
        return enfants


    def mutation(self, enfants):
        """Mutation des gènes spontanée de la nouvelle génération."""
        for enfant in enfants:
            enfant.muter(self.val_min, self.val_max, self.p_mut)

    def nouvelle_génération(self, enfants):
        """Création d'une nouvelle génération."""
        self.individus = enfants
        self.actualisation_fitness()

    def élitisme(self, nouvelle_génération):
        """Remplace le pire enfant par le meilleur individu de la précédente génération."""
        pire = max(nouvelle_génération, key=lambda ind: ind.pondération)
        meilleur = self.meilleur_individu()
        nouvelle_génération.remove(pire)
        nouvelle_génération.append(meilleur)
        return nouvelle_génération

    def __repr__(self):
        """Représentation lisible de la population."""
        return f"Population:\n" + "\n".join([str(ind) for ind in self.individus])

