'''
Ce fichier implémente toutes les fonctions nécessaires à la vérification et l'analyse des voeux ainsi qu'à la répartition des auditeurs.

Auteur: Vincent O'Luasa
Contact: vincent.oluasa@gmail.com
Date d'écriture: Juillet 2024

Ces fonctions sont basées sur le travail de Paul Simon, AdJ. 2019
Contact: paul.dc.simon@gmail.com
'''
from __future__ import annotations

import numpy as np
import streamlit as st
import pandas as pd
import os
from collections import Counter
from villes import Ville
from typing import Dict, List, Tuple, Union, Any, Optional

########################################################################################################################
# Fonctions pour la vérification des voeux
########################################################################################################################

def verifier_existance_voeux(list_voeux: List[str], 
                           villes: Dict[str, Ville]) -> Tuple[bool, List[str]]:
    """Vérifie si tous les voeux de la liste correspondent à des villes existantes.

    Args:
        list_voeux (List[str]): Liste des noms de villes représentant les voeux
        villes (Dict[str, Ville]): Dictionnaire des villes disponibles avec leurs objets Ville

    Returns:
        Tuple contenant :
            - succes (bool): True si tous les voeux existent, False sinon
            - inconnues (List[str]): Liste des noms de villes inconnus
    """
    succes = True
    inconnues = []
    for v in list_voeux:
        if not (v in villes):
            succes = False
            inconnues.append(v)
    return succes, inconnues


def verifier_unicite_voeux(list_voeux: List[str]) -> bool:
    """Vérifie qu'il n'y a pas de doublons dans la liste de voeux.

    Args:
        list_voeux (List[str]): Liste des noms de villes représentant les voeux

    Returns:
        bool: True si tous les voeux sont uniques, False s'il y a des doublons
    """
    return len(set(list_voeux)) == len(list_voeux)


def compte_rouge(list_voeux: List[str], 
                 villes_rouges: List[str]) -> int:
    """Compte le nombre de villes rouges dans la liste de voeux.

    Args:
        list_voeux (List[str]): Liste des noms de villes représentant les voeux
        villes_rouges (List[str]): Liste des noms de villes rouges

    Returns:
        int: Nombre de villes rouges dans les voeux
    """
    n = 0
    for x in list_voeux:
        if x in villes_rouges:
            n += 1
    return n


def compte_noir(list_voeux: List[str], 
                villes_noires: List[str]) -> int:
    """Compte le nombre de villes noires dans la liste de voeux.

    Args:
        list_voeux (List[str]): Liste des noms de villes représentant les voeux
        villes_noires (List[str]): Liste des noms de villes noires

    Returns:
        int: Nombre de villes noires dans les voeux
    """
    n = 0
    for x in list_voeux:
        if x in villes_noires:
            n += 1
    return n


def compte_vert(list_voeux: List[str], 
                villes_vertes: List[str]) -> int:
    """Compte le nombre de villes vertes dans la liste de voeux.

    Args:
        list_voeux (List[str]): Liste des noms de villes représentant les voeux
        villes_vertes (List[str]): Liste des noms de villes vertes

    Returns:
        int: Nombre de villes vertes dans les voeux
    """
    n = 0
    for x in list_voeux:
        if x in villes_vertes:
            n += 1
    return n


def verification_voeux(voeux_df: pd.DataFrame, 
                      postes_df: pd.DataFrame, 
                      params_dict: Dict[str, Any]) -> Tuple[int, int, int]:
    """Vérifie tous les voeux par rapport aux contraintes et règles spécifiées.

    Cette fonction vérifie :
    1. Le nombre de voeux par auditeur (minimum et maximum)
    2. L'existence des villes souhaitées
    3. L'unicité des voeux
    4. Les règles de distribution des couleurs (noires, rouges, vertes)
    5. Écrit les erreurs dans un fichier de log 'voeux_non_valides.txt'
    6. Modifie le DataFrame des voeux en invalidant les voeux non conformes

    Args:
        voeux_df (pd.DataFrame): DataFrame contenant les voeux des auditeurs
        postes_df (pd.DataFrame): DataFrame contenant les informations des TJs
        params_dict (Dict[str, Any]): Dictionnaire contenant les paramètres de configuration :
            - Voeux : Nombre de voeux par auditeur
            - Noires max : Nombre maximum de villes noires
            - Noires ou rouges max : Nombre maximum de villes rouges ou noires
            - Vertes min : Nombre minimum de villes vertes

    Returns:
        Tuple contenant :
            - erreurs (int): Nombre de voeux invalides
            - valides (int): Nombre de voeux valides
            - trop_de_voeux (int): Nombre d'auditeurs avec plus de voeux que le maximum autorisé
    """
    voeux = params_dict["Voeux"]
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
    
    # Création et/ou ouverture du fichier de log des voeux non valides
    log_file = "logs/voeux_non_valides.txt"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "w") as f:
        for index, row in voeux_df.iterrows():
            aud = str(row["id_auditeur"])
            voeux_aud = row[1:].dropna().values

            succes, inconnues = verifier_existance_voeux(voeux_aud, villes)
            n_noir = compte_noir(voeux_aud[:voeux], villes_noires)
            n_rouge = compte_rouge(voeux_aud[:voeux], villes_rouges)
            n_vert = compte_vert(voeux_aud[:voeux], villes_vertes)

            if len(voeux_aud) < voeux:
                f.write(f"Auditeur {aud}:\tERREUR ! Pas assez de voeux.\n")
                voeux_df.iloc[index, 1:] = np.nan
                erreurs += 1
            elif not (succes):
                f.write(f"Auditeur {aud}:\tERREUR ! Voeu(x) inconnu(s) :\t{inconnues}\n")
                voeux_df.iloc[index, 1:] = np.nan
                erreurs += 1
            elif not (verifier_unicite_voeux(voeux_aud)):
                f.write(f"Auditeur {aud}:\tERREUR ! Doublons :\t{voeux_aud}\n")
                voeux_df.iloc[index, 1:] = np.nan
                erreurs += 1
            elif (
                (n_noir > noires_max)
                or (n_noir + n_rouge > rouges_noires_max)
                or (n_vert < vertes_min)
            ):
                f.write(
                    f"Auditeur {aud}:\tERREUR ! Couleurs ({n_noir} N, {n_rouge} R, {n_vert} V)\t\n"
                )
                voeux_df.iloc[index, 1:] = np.nan
                erreurs += 1
            else:
                valides += 1
                if len(voeux_aud) > voeux:
                    trop_de_voeux += 1
    return erreurs, valides, trop_de_voeux

########################################################################################################################
# Fonction qui analyse la distribution des voeux
########################################################################################################################

def distribution_des_voeux(villes: Dict[str, Ville], 
                          voeux_df: pd.DataFrame, 
                          postes_df: pd.DataFrame, 
                          voeux: int) -> Tuple[pd.DataFrame, int]:
    """Analyse la distribution des voeux entre les villes et les postes.

    Cette fonction :
    1. Calcule la distribution des voeux par TJ
    2. Identifie les postes non demandés
    3. Met à jour le DataFrame des postes avec les données de distribution des voeux

    Args:
        villes (Dict[str, Ville]): Dictionnaire d'objets Ville représentant chaque TJ
        voeux_df (pd.DataFrame): DataFrame contenant les voeux des auditeurs
        postes_df (pd.DataFrame): DataFrame contenant les informations des TJs
        voeux (int): Nombre de voeux par auditeur

    Returns:
        Tuple contenant :
            - postes_df (pd.DataFrame): DataFrame mise à jour avec l'analyse de la distribution des voeux
            - nb_postes_non_demandes (int): Nombre de postes qui n'ont pas été demandés
    """
    print("\nEtude de la distribution des voeux:")
    for i in range(1, voeux+2):
        postes_df[f"nombre_voeux_{i}"] = np.nan
    nb_postes_non_demandes = 0
    
    for i in range(1, voeux_df.shape[1]+1):
        voeux_i = dict(Counter(voeux_df[f'v_{i}'].dropna().values))
        for ville in voeux_i:
            if i-1 < voeux:
                postes_df.loc[postes_df['Ville'] == ville, f"nombre_voeux_{i}"] = voeux_i[ville]
            else:
                postes_df.loc[postes_df['Ville'] == ville, f"nombre_voeux_{voeux+1}"] = voeux_i[ville]
    postes_df['total_demandes'] = postes_df[[f"nombre_voeux_{i}" for i in range(1, voeux+2)]].sum(axis=1)
    
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

def voeu_vers_cout(num_voeu: int, methode: str) -> float:
    """Convertit un numéro de voeu en coût selon la méthode spécifiée.

    Args:
        num_voeu (int): Position du voeu dans la liste de l'auditeur
        methode (str): Méthode de calcul des coûts ('linéaire', 'carré', ou 'exp')

    Returns:
        float: Coût calculé pour le voeu

    Raises:
        ValueError: Si une méthode inconnue est spécifiée
    """
    if methode == 'linéaire':
        return num_voeu
    elif methode == 'carré':
        return num_voeu * num_voeu
    elif methode == 'exp':
        return np.exp(num_voeu)
    else:
        raise ValueError(f"Méthode inconnue: {methode}")


def creer_matrice_couts(nb_auditeurs: int, 
                       nb_postes: int, 
                       repartition_df: pd.DataFrame, 
                       villes: Dict[str, Ville], 
                       params_dict: Dict[str, Any], 
                       methode: str) -> np.ndarray:
    """Crée une matrice de coûts pour le problème d'affectation.

    La matrice de coûts représente le coût d'affecter chaque auditeur à chaque poste,
    en fonction de leurs voeux et de la méthode de calcul des coûts spécifiée.

    Args:
        nb_auditeurs (int): Nombre total d'auditeurs
        nb_postes (int): Nombre total de postes disponibles
        repartition_df (pd.DataFrame): DataFrame contenant les voeux des auditeurs
        villes (Dict[str, Ville]): Dictionnaire d'objets Ville
        params_dict (Dict[str, Any]): Dictionnaire contenant les paramètres de configuration
        methode (str): Méthode de calcul des coûts à utiliser

    Returns:
        np.ndarray: Matrice de coûts de dimension (nb_auditeurs, nb_postes)
    """
    # voeux_max = params_dict['Voeux max']
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
                matrice_couts[ligne, col] = cout
    return matrice_couts


def recuperer_num_voeu(voeux: np.ndarray, assignation: str) -> int:
    """Trouve la position d'une ville assignée dans la liste de voeux d'un auditeur.

    Args:
        voeux (np.ndarray): Tableau des noms de villes représentant les voeux d'un auditeur
        assignation (str): Nom de la ville assignée

    Returns:
        int: Numero du voeux correpondant à la ville assignée, 100 si hors voeux
    """
    indices = np.where(voeux == assignation)[0]
    if len(indices) == 0:
        return 100
    else:
        return indices[0] + 1
