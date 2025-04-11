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
from collections import Counter
from villes import Ville
from typing import Dict, List, Tuple, Union, Any, Optional

########################################################################################################################
# Fonctions pour la vérification des voeux
########################################################################################################################

def verifier_existance_voeux(list_voeux: List[str], 
                           villes: Dict[str, Ville]) -> Tuple[bool, List[str]]:
    """Verify if all wishes in the list correspond to existing cities.

    Args:
        list_voeux (List[str]): List of city names representing wishes
        villes (Dict[str, Ville]): Dictionary of available cities with their Ville objects

    Returns:
        Tuple containing:
            - succes (bool): True if all wishes exist, False otherwise
            - inconnues (List[str]): List of unknown city names
    """
    succes = True
    inconnues = []
    for v in list_voeux:
        if not (v in villes):
            succes = False
            inconnues.append(v)
    return succes, inconnues


def verifier_unicite_voeux(list_voeux: List[str]) -> bool:
    """Verify that there are no duplicate wishes in the list.

    Args:
        list_voeux (List[str]): List of city names representing wishes

    Returns:
        bool: True if all wishes are unique, False if there are duplicates
    """
    return len(set(list_voeux)) == len(list_voeux)


def compte_rouge(list_voeux: List[str], 
                 villes_rouges: List[str]) -> int:
    """Count the number of red cities in the list of wishes.

    Args:
        list_voeux (List[str]): List of city names representing wishes
        villes_rouges (List[str]): List of red city names

    Returns:
        int: Number of red cities in the wishes
    """
    n = 0
    for x in list_voeux:
        if x in villes_rouges:
            n += 1
    return n


def compte_noir(list_voeux: List[str], 
                villes_noires: List[str]) -> int:
    """Count the number of black cities in the list of wishes.

    Args:
        list_voeux (List[str]): List of city names representing wishes
        villes_noires (List[str]): List of black city names

    Returns:
        int: Number of black cities in the wishes
    """
    n = 0
    for x in list_voeux:
        if x in villes_noires:
            n += 1
    return n


def compte_vert(list_voeux: List[str], 
                villes_vertes: List[str]) -> int:
    """Count the number of green cities in the list of wishes.

    Args:
        list_voeux (List[str]): List of city names representing wishes
        villes_vertes (List[str]): List of green city names

    Returns:
        int: Number of green cities in the wishes
    """
    n = 0
    for x in list_voeux:
        if x in villes_vertes:
            n += 1
    return n


def verification_voeux(voeux_df: pd.DataFrame, 
                      postes_df: pd.DataFrame, 
                      params_dict: Dict[str, Any]) -> Tuple[int, int, int]:
    """Verify all wishes against the specified constraints and rules.

    This function checks:
    1. Number of wishes per auditor
    2. Existence of wished cities
    3. Uniqueness of wishes
    4. Color distribution rules

    Args:
        voeux_df (pd.DataFrame): DataFrame containing auditors' wishes
        postes_df (pd.DataFrame): DataFrame containing TJs information
        params_dict (Dict[str, Any]): Dictionary containing configuration parameters:
            - Voeux max: Maximum number of wishes per auditor
            - Noires max: Maximum number of black cities
            - Noires ou rouges max: Maximum number of black or red cities
            - Vertes min: Minimum number of green cities

    Returns:
        Tuple containing:
            - erreurs (int): Number of invalid wishes
            - valides (int): Number of valid wishes
            - trop_de_voeux (int): Number of auditors with too many wishes
    """
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

def distribution_des_voeux(villes: Dict[str, Ville], 
                          voeux_df: pd.DataFrame, 
                          postes_df: pd.DataFrame, 
                          voeux_max: int) -> Tuple[pd.DataFrame, int]:
    """Analyze the distribution of wishes across cities and positions.

    This function:
    1. Counts wishes for each city and position
    2. Identifies undemanded positions
    3. Updates the postes DataFrame with wish distribution data

    Args:
        villes (Dict[str, Ville]): Dictionary of Ville objects representing each TJ
        voeux_df (pd.DataFrame): DataFrame containing auditors' wishes
        postes_df (pd.DataFrame): DataFrame containing TJs information
        voeux_max (int): Maximum number of wishes per auditor

    Returns:
        Tuple containing:
            - postes_df (pd.DataFrame): Updated DataFrame with wish distribution analysis
            - nb_postes_non_demandes (int): Number of positions that were not requested
    """
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

def voeu_vers_cout(num_voeu: int, methode: str) -> float:
    """Convert a wish number to a cost based on the specified method.

    Args:
        num_voeu (int): Position of the wish in the auditor's list (1-based)
        methode (str): Cost calculation method ('linéaire', 'carré', or 'exp')

    Returns:
        float: Calculated cost for the wish

    Raises:
        ValueError: If an unknown method is specified
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
    """Create a cost matrix for the assignment problem.

    The cost matrix represents the cost of assigning each auditor to each position,
    based on their wishes and the specified cost calculation method.

    Args:
        nb_auditeurs (int): Total number of auditors
        nb_postes (int): Total number of available positions
        repartition_df (pd.DataFrame): DataFrame containing auditors' wishes
        villes (Dict[str, Ville]): Dictionary of Ville objects
        params_dict (Dict[str, Any]): Dictionary containing configuration parameters
        methode (str): Cost calculation method to use

    Returns:
        np.ndarray: Cost matrix of shape (nb_auditeurs, nb_postes)
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
    """Find the position of an assigned city in an auditor's wish list.

    Args:
        voeux (np.ndarray): Array of city names representing an auditor's wishes
        assignation (str): Assigned city name

    Returns:
        int: Position of the assigned city in the wish list (1-based), or 100 if not found
    """
    indices = np.where(voeux == assignation)[0]
    if len(indices) == 0:
        return 100
    else:
        return indices[0] + 1
