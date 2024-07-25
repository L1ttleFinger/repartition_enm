'''
Ce fichier implémente toutes les fonctions nécessaires à la vérification et l'analyse des voeux ainsi qu'à la répartition des auditeurs.

Auteur: Vincent O'Luasa
Contact: vincent.oluasa@gmail.com
Date d'écriture: Juillet 2024

Ces fonctions sont basées sur le travail de Paul Simon, AdJ. 2019
Contact: paul.dc.simon@gmail.com
'''

import numpy as np
import streamlit as st
from collections import Counter

########################################################################################################################
# Fonctions pour la vérification des voeux
########################################################################################################################

def verifier_existance_voeux(l, villes):
    succes = True
    inconnues = []
    for v in l:
        if not (v in villes):
            succes = False
            inconnues.append(v)
    return succes, inconnues


def verifier_unicite_voeux(l):
    return len(set(l)) == len(l)


def compte_rouge(l, villes_rouges):
    n = 0
    for x in l:
        if x in villes_rouges:
            n = n + 1
    return n


def compte_noir(l, villes_noires):
    n = 0
    for x in l:
        if x in villes_noires:
            n = n + 1
    return n


def compte_vert(l, villes_vertes):
    n = 0
    for x in l:
        if x in villes_vertes:
            n = n + 1
    return n


def verification_voeux(voeux_df, postes_df, params_dict):
    voeux_max = params_dict["Voeux max"]
    noires_max = params_dict["Noires max"]
    rouges_noires_max = params_dict["Noires ou rouges max"]
    vertes_min = params_dict["Vertes min"]

    villes = postes_df["Ville"].unique()
    villes_noires = postes_df[postes_df["Couleur"] == "noir"]["Ville"].unique()
    villes_rouges = postes_df[postes_df["Couleur"] == "rouge"]["Ville"].unique()
    villes_vertes = postes_df[postes_df["Couleur"] == "vert"]["Ville"].unique()

    erreurs = 0
    valides = 0
    trop_de_voeux = 0
    for index, row in voeux_df.iterrows():
        aud = str(row["id_auditeur"])
        voeux_aud = row[1:].dropna().values

        succes, inconnues = verifier_existance_voeux(voeux_aud, villes)
        n_noir = compte_noir(voeux_aud[:voeux_max], villes_noires)
        n_rouge = compte_rouge(voeux_aud[:voeux_max], villes_rouges)
        n_vert = compte_vert(voeux_aud[:voeux_max], villes_vertes)

        if len(voeux_aud) < voeux_max:
            print(f"Auditeur {aud}:\tERREUR ! Pas assez de voeux.")
            voeux_df.iloc[index, 1:] = np.nan
            erreurs += 1
        elif not (succes):
            print(f"Auditeur {aud}:\tERREUR ! Voeu(x) inconnu(s) :\t", inconnues)
            voeux_df.iloc[index, 1:] = np.nan
            erreurs += 1
        elif not (verifier_unicite_voeux(voeux_aud)):
            print(f"Auditeur {aud}:\tERREUR ! Doublons :\t", voeux_aud)
            voeux_df.iloc[index, 1:] = np.nan
            erreurs += 1
        elif (
            (n_noir > noires_max)
            or (n_noir + n_rouge > rouges_noires_max)
            or (n_vert < vertes_min)
        ):
            print(
                f"Auditeur {aud}:\tERREUR ! Couleurs ({n_noir} N, {n_rouge} R, {n_vert} V)\t"
            )
            voeux_df.iloc[index, 1:] = np.nan
            erreurs += 1
        else:
            valides += 1
            if len(voeux_aud) > voeux_max:
                trop_de_voeux += 1
    return erreurs, valides, trop_de_voeux

########################################################################################################################
# Fonction qui analyse la distribution des voeux
########################################################################################################################

def distribution_des_voeux(villes, voeux_df, postes_df, voeux_max):
    print("\nEtude de la distribution des voeux:")
    for i in range(1, voeux_max+2):
        postes_df[f"nombre_voeux_{i}"] = np.nan
    nb_postes_non_demandes = 0
    
    for i in range(1, voeux_df.shape[1]+1):
        voeux_i = dict(Counter(voeux_df[f'v_{i}'].dropna().values))
        for ville in voeux_i:
            if i-1 < voeux_max:
                postes_df.loc[postes_df['Ville'] == ville, f"nombre_voeux_{i}"] = voeux_i[ville]
            else:
                postes_df.loc[postes_df['Ville'] == ville, f"nombre_voeux_{voeux_max+1}"] = voeux_i[ville]
    postes_df['total_demandes'] = postes_df[[f"nombre_voeux_{i}" for i in range(1, voeux_max+2)]].sum(axis=1)
    
    for ville in postes_df[postes_df['total_demandes'] == 0]['Ville']:
        capacite = villes[ville].capacite
        print(f"Aucun auditeur n'a placé {ville} dans ses voeux ({capacite} places)")
        nb_postes_non_demandes = nb_postes_non_demandes + capacite
    
    st.write(
        f"Il y a {nb_postes_non_demandes} postes qui n'ont été demandés par personne."
    )
    return postes_df, nb_postes_non_demandes

########################################################################################################################
# Fonctions de création de la matrice des couts et de récupération du numéro d'un voeu en fonction de la ville assignée
########################################################################################################################

def voeu_vers_cout(num_voeu, methode):
    if methode == 'linéaire':
        return num_voeu
    elif methode == 'carré':
        return num_voeu * num_voeu
    elif methode == 'exp':
        return np.exp(num_voeu)


def creer_matrice_couts(nb_auditeurs, nb_postes, repartition_df, villes, params_dict, methode):
    voeux_max = params_dict['Voeux max']
    penalite = params_dict['Penalite']
    # lignes : nb_auditeurs ; colonnes : nb_postes
    matrice_couts = np.full((nb_auditeurs, nb_postes), penalite)

    # Remplissage de la matrice :
    # pour chaque auditeur, on regarde les voeux dans l'ordre :
    # pour chaque voeu, on met un nombre correspondant à l'ordre dans toutes les colonnes de la ville

    for ligne, row in repartition_df.iterrows():
        voeux_aud = row[1:].dropna().values
        for num_voeu in range(len(voeux_aud)):
            voeu_actuel = voeux_aud[num_voeu]
            colonnes = villes[voeu_actuel].colonnes
            for col in colonnes:
                cout = voeu_vers_cout(num_voeu, methode)
                if num_voeu > (voeux_max - 1):
                    cout *= 10
                matrice_couts[ligne, col] = cout
    return matrice_couts


def recuperer_num_voeu(voeux, assignation):
    indices = np.where(voeux == assignation)[0]
    if len(indices) == 0:
        return 100
    else:
        return indices[0] + 1
########################################################################################################################
########################################################################################################################