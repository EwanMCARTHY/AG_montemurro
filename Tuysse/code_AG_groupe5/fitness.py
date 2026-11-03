# -*- Coding: utf-8 -*-
"""
Created on Wed Nov 27 11:26:39 2024

@author: niCol
"""

import numpy as np
import math


# Calcul de la matrice de rotation d'un pli vers le repère Cartésien
#On renvoie l'inverse de la matrice de rotation, c'est elle qui nous sera utile


def inv_rotation(theta):
    """Prend en entrée l'angle theta du pli
    Renvoie l'inverse de la matrice de rotation associée"""
    R = np.zeros((6, 6))                        # Initialisation de la matrice de rotation 6x6
    theta_rad = np.radians(theta)               # Les fonctions cos et sin prennent un argument en radians
    c, s = np.cos(theta_rad), np.sin(theta_rad)
    R[0, 0] = c ** 4
    R[0, 1] = -4 * s * c ** 3
    R[0, 2] = 2 * s ** 2 * c ** 2
    R[0, 3] = 4 * s ** 2 * c ** 2
    R[0, 4] = -4 * s ** 3 * c
    R[0, 5] = s ** 4
    R[1, 0] = -s * c ** 3
    R[1, 1] = c ** 4 - 3 * s ** 2 * c ** 2
    R[1, 2] = s * c ** 3 - s ** 3 * c
    R[1, 3] = 2 * (s * c ** 3 - s ** 3 * c)
    R[1, 4] = 3 * s ** 2 * c ** 2 - s ** 4
    R[1, 5] = s ** 3 * c
    R[2, 0] = s ** 2 * c ** 2
    R[2, 1] = 2 * (s ** 3 * c - s * c ** 3)
    R[2, 2] = c ** 4 + s ** 4
    R[2, 3] = -4 * s ** 2 * c ** 2
    R[2, 4] = 2 * (s * c ** 3 - s ** 3 * c)
    R[2, 5] = s ** 2 * c ** 2
    R[3, 0] = s ** 2 * c ** 2
    R[3, 1] = 2 * (s ** 3 * c - s * c ** 3)
    R[3, 2] = -2 * s ** 2 * c ** 2
    R[3, 3] = (c ** 2 - s ** 2) ** 2
    R[3, 4] = 2 * (s * c ** 3 - s ** 3 * c)
    R[3, 5] = s ** 2 * c ** 2
    R[4, 0] = -s ** 3 * c
    R[4, 1] = 3 * s ** 2 * c ** 2 - s ** 4
    R[4, 2] = s ** 3 * c - s * c ** 3
    R[4, 3] = 2 * (s ** 3 * c - s * c ** 3)
    R[4, 4] = c ** 4 - 3 * s ** 2 * c ** 2
    R[4, 5] = s * c ** 3
    R[5, 0] = s ** 4
    R[5, 1] = -4 * s ** 3 * c
    R[5, 2] = 2 * s ** 2 * c ** 2
    R[5, 3] = 4 * s ** 2 * c ** 2
    R[5, 4] = -4 * s * c ** 3
    R[5, 5] = c ** 4
    
    return np.linalg.inv(R)

#Calcul de la mattrice de rigidité réduite du pli considéré, à partir des données de l'énnoncé


def Q(E1, E2, n12, G12): # E1, E2 : Modules d'élasticité dans les directions principales ; n12 : Coefficient de Poisson ; G12 : Module de cisaillement
    Q = np.zeros((3, 3)) #on calcule la matrice de rigidité dans le plan

    n21 =E2*(n12/E1) # Calcul du coefficient de Poisson réciproque
    
    Q[0, 0] = E1 /(1-(n12*n21))
    Q[0, 1] = n12*E2/(1-(n12*n21))
    Q[1, 0] = n12 *E2/ (1-(n12*n21))
    Q[1, 1] = E2/(1-(n12*n21))
    Q[2, 2] = G12

    return Q

#définition de la notation de Voigt, passage d'une matrice 6*6 
#à un vecteur (1,6)

def Voigt(Q):
    Vo = np.zeros(6)
    Vo[0] = Q[0, 0]
    Vo[1] = Q[1, 1]
    Vo[2] = Q[2, 2]
    Vo[3] = Q[1, 2]
    Vo[4] = Q[0, 2]
    Vo[5] = Q[0, 1]
    return Vo



def Z(n_plis,tpli):  # Permet de calculer les Zk du stratifié pour un nombre de plis n_plis et une épaisseur de pli tpli
    Z=[]
    if n_plis%2 == 1:
        for i in range(n_plis):
            Z.append((i-int((n_plis/2+1)+1/2))*tpli) 
    else:
        for i in range(n_plis):
            Z.append((i-int(n_plis/2))*tpli) 
    return Z


# Calcul du tenseur de rigidité de membrane dans le cas d'un stratifié avec des plis
#d'épaisseur uniforme


def A(Liste_Q,k,e_pli): # Liste_Q : Liste des matrices de rigidité réduite pour chaque pli ; k : Nombre de plis ; e_pli : Épaisseur d'un pli
    
    A = np.zeros(6)
    for i in range(k):
        A += e_pli*Liste_Q[i]
        
        
    return  A # Tenseur de rigidité de membrane

# Calcul du tenseur de couplage membrane/flexion  B 
# Avec la définition des coefficients bk du cours en traitant les cas 
#des nombres de plis pairs et impair

def B(e_pli, matrices_Qt,Z): #  matrices_Qt : Liste des matrices de rigidité transformées ; Z : Coordonnées des couches
    B=np.zeros(6)
    n_pli=len(matrices_Qt)
    for i in range(n_pli-1):
        B+= (Z[i+1]**2 - Z[i]**2)*matrices_Qt[i]
        
        
    return(B) # Tenseur de couplage membrane/flexion


#Même chose pour le calcul du tenseur de rigidité en flexion D avec les coefficients 
#dk à différencier selon le cas du nombre de plis pair ou impair

def D(e_pli, matrices_Qt,Z):
    D = np.zeros(6)
    n = len(matrices_Qt)
    for i in range(n-1):
        D+= 1/3 *((Z[i+1]**3 - Z[i]**3)*matrices_Qt[i])
    
    return(D) # Tenseur de rigidité en flexion


def parametres_polaires(V):
    """ Prend en entrée les matrices Q,A,B,D en notation de Voigt
    Renvoie leur paramètres polaires"""
    
    
    T0 = (V[0] - 2 * V[2] + 4 * V[3] + V[5] ) /8
    T1 = (V[0] + 2 * V[2]  + V[5] ) /8
    R0 = math.sqrt((V[0] - 2 * V[2] - 4 * V[3] + V[5])**2 + (4 * V[1] - 4 * V[4] )**2 ) /8
    R1 = math.sqrt((V[0] -  V[5])**2 + (2 * V[1] + 2 * V[4] )**2 ) /8
    Phi0 = math.atan2(4 * V[1] - 4 * V[4], V[0] - 2 * V[2] - 4 * V[3] + V[5]) / 4
    Phi1 = math.atan2(2 * V[1] + 2 * V[4], V[0] -  V[5]) / 2

    
    return T0,T1,R0,R1,Phi0,Phi1

# Calcul de la norme
def norme(V):
    """Prend en entrée une matrice en Notation de Voigt
    Renvoie la norme associée"""
    
    (T0, T1, R0, R1, phi0, phi1) = parametres_polaires(V)#calcul des paramètres polaires du vecteur
    return math.sqrt(T0 ** 2 + 2 * T1 ** 2 + R0 ** 2 + 4 * R1 ** 2)

def phi_1(Bs, h, Q):
   
    return (norme(Bs) / norme(Q)) ** 2


# Homogénéité (C=A*-D*=0)
def phi_2(C, Q):
    return (norme(C) / norme(Q)) ** 2

#Isotropie 
def phi_6(As, h,Q_V):
    (T0_A, T1_A, R0_A, R1_A, phi0_A, phi1_A) = parametres_polaires(As)
    R0,R1 = parametres_polaires(Q_V)[2], parametres_polaires(Q_V)[3]
    
    return ((R0_A)**2 + 4*(R1_A)**2)/((R0)**2 + 4*(R1)**2) 

# isotropie en flexion 

def phi_10(Ds,h,Q_V):
    (T0_D_etoile, T1_D_etoile, R0_D_etoile, R1_D_etoile, phi0_D_etoile, phi1_D_etoile) = parametres_polaires(Ds)
    R0,R1 = parametres_polaires(Q_V)[2], parametres_polaires(Q_V)[3]
    
    return (((R0_D_etoile)**2 +4*(R1_D_etoile)**2)/((R0)**2+4*(R1)**2)) 

# Objectif total
def phi_tot(As, Bs, C, h, Q_V):
    return phi_1(Bs, h, Q_V) + phi_2(C, Q_V) + phi_6(As, h,Q_V)  #+phi_10(D, h,Q_base) 


    
    
    
