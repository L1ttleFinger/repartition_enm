'''
Ce fichier implémente 2 fonctions:
    - verification_et_analyse_des_voeux: En charge de la vérification et d'analyse des voeux,
    - executer_la_repartition: En charge de la répartition des auditeurs.

Auteur: Vincent O'Luasa
Contact: vincent.oluasa@gmail.com
Date d'écriture: Juillet 2024

Ces fonctions sont basées sur le travail de Paul Simon, AdJ. 2019
Contact: paul.dc.simon@gmail.com
'''
from __future__ import annotations

import numpy as np
import os
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from scipy import optimize
from utils import *
from villes import Ville
from typing import Dict, Tuple, List, Any, Union

seed = 42
RESULTS_PATH = "./resultats/"
if not os.path.exists(RESULTS_PATH):
    os.makedirs(RESULTS_PATH)

def verification_et_analyse_des_voeux(postes_df: pd.DataFrame, 
                                      voeux_df: pd.DataFrame, 
                                      params_dict: Dict[str, Any]) -> Tuple[Dict[str, Ville], pd.DataFrame, pd.DataFrame, int, int, plt.Figure, plt.Figure, plt.Figure]:
    """Analyze and verify the wishes of auditors and prepare data for distribution.

    This function performs several key tasks:
    1. Verifies the validity of wishes against constraints
    2. Analyzes the distribution of wishes
    3. Generates visualizations of the data
    4. Prepares data for the distribution process

    Args:
        postes_df (pd.DataFrame): DataFrame containing TJs (Tribunaux Judiciaires) information including:
            - Ville: City name
            - Postes: Number of available positions
            - Couleur: Color classification of the city
        voeux_df (pd.DataFrame): DataFrame containing auditors' wishes with columns:
            - id_auditeur: Auditor ID
            - v_1, v_2, etc.: Wish columns for each position
        params_dict (Dict[str, Any]): Dictionary containing configuration parameters:
            - Voeux max: Maximum number of wishes per auditor
            - Noires max: Maximum number of black cities
            - Noires ou rouges max: Maximum number of black or red cities
            - Vertes min: Minimum number of green cities
            - Methodes: List of cost calculation methods
            - Penalite: Default penalty for post assignments

    Returns:
        Tuple containing:
            - villes (Dict[str, Ville]): Dictionary of Ville objects representing each TJ
            - postes_df (pd.DataFrame): Updated postes DataFrame with wish distribution analysis
            - voeux_df (pd.DataFrame): Updated voeux DataFrame after verification
            - nb_postes (int): Total number of available positions
            - nb_auditeurs (int): Total number of auditors
            - top_30_demandes (plt.Figure): Figure showing top 30 most requested cities
            - top_30_voeux1 (plt.Figure): Figure showing top 30 first-choice cities
            - taux_assignation (plt.Figure): Figure showing assignment rate analysis
    """
    voeux_max = params_dict["Voeux max"]
    nb_postes = postes_df["Postes"].sum()

    villes = {}  # dictionnaire de Villes qui contient toutes les villes
    for index, row in postes_df.iterrows():
        if row["Postes"] > 0:
            villes[row["Ville"]] = Ville(index, row["Ville"], row["Postes"])
        else:
            st.write("Ville ignorée (aucun poste) :", row["Ville"])
    
    st.write(f"Il y a {nb_postes} postes disponibles dans {len(postes_df)} villes.")
    st.divider()

    # Vérification des voeux
    st.write("Critères de validation des voeux:\n"
             + "\n- Nombre de voeux suffisant,"
             + "\n- Existence de chaque ville souhaitée,"
             + "\n- Unicité des voeux,"
             + "\n- Respect des règles de couleur."
    )

    erreurs, valides, trop_de_voeux = verification_voeux(voeux_df, postes_df, params_dict)

    st.write(
        f"Voeux valides: {valides} | Voeux invalides: {erreurs}."
    )
    if trop_de_voeux > 0:
        st.write(
            f"{trop_de_voeux} auditeurs sur {valides} ont formulé plus de {voeux_max} voeux"
        )
    st.divider()

    nb_auditeurs = len(voeux_df)

    st.write(
        f"Il y a {nb_auditeurs} auditeurs à répartir sur {nb_postes} postes.\n"
    )
    marge = nb_postes - nb_auditeurs

    # Traitement des cas particuliers
    voeux_df.set_index('id_auditeur', inplace=True)

    # Calcul du nombre de villes n'ayant été demandées par personne :
    postes_df, nb_postes_non_demandes = distribution_des_voeux(villes, voeux_df, postes_df, voeux_max)
    postes_df.to_csv(os.path.join(RESULTS_PATH, 'distribution_voeux.csv'), index=False)

    if (nb_postes_non_demandes > marge) or (erreurs > 0):
        st.write(
            f"Il y aura donc forcément au moins {max(nb_postes_non_demandes - marge, erreurs)} auditeurs placés hors de leurs voeux :(\n(dont {erreurs} pour cause de voeux invalides)."
        )

    top_30_demandes, ax1 = plt.subplots(1, 1)
    top_30_voeux1, ax2 = plt.subplots(1, 1)
    ax_demandes = postes_df.sort_values(by='total_demandes', ascending=False).set_index('Ville').head(30)[['total_demandes', 'Postes']].plot.bar(figsize=(10,5), ax=ax1, xlabel='')
    ax_demandes.bar_label(ax_demandes.containers[0])
    ax_voeux = postes_df.sort_values(by='nombre_voeux_1', ascending=False).set_index('Ville').head(30)[['nombre_voeux_1', 'Postes']].plot.bar(figsize=(10,5), ax=ax2, xlabel='')
    ax_voeux.bar_label(ax_voeux.containers[0])
    ax1.legend(["Nombre de voeux", "Nombre de postes"])
    ax2.legend(["Nombre de 1er voeux", "Nombre de postes"])

    # Taux d'assignation
    assignment_rates = {}
    for nb_voeux in range(1,voeux_max+1):
        cols = [f'nombre_voeux_{i}' for i in range(1, nb_voeux+1)]
        rate = min(100 * postes_df.dropna(how='all', subset=cols)['Postes'].sum() / nb_auditeurs, 100)
        assignment_rates[nb_voeux] = rate
    taux_assignation, ax_rates = plt.subplots()
    bar_container = ax_rates.bar(range(len(assignment_rates)), list(assignment_rates.values()), align='center')
    ax_rates.bar_label(bar_container, fmt='{:,.1f}')
    plt.xticks(range(len(assignment_rates)), list(assignment_rates.keys()))
    plt.ylim(60,103)

    return villes, postes_df, voeux_df, nb_postes, nb_auditeurs, top_30_demandes, top_30_voeux1, taux_assignation


def executer_la_repartition(villes: Dict[str, Ville], 
                            original_voeux_df: pd.DataFrame, 
                            nb_auditeurs: int, 
                            nb_postes: int, 
                            params_dict: Dict[str, Union[int, List[str]]], 
                            methode: str, 
                            file_name: str | None = None) -> Tuple[pd.DataFrame, plt.Figure, float, float, float]:
    """Execute the distribution of auditors to positions using the specified method.

    This function:
    1. Creates a cost matrix based on wishes and constraints
    2. Uses linear sum assignment to find optimal distribution
    3. Generates results and visualizations
    4. Saves results to CSV

    Args:
        villes (Dict[str, Ville]): Dictionary of Ville objects representing each TJ
        original_voeux_df (pd.DataFrame): DataFrame containing auditors' wishes
        nb_auditeurs (int): Total number of auditors to distribute
        nb_postes (int): Total number of available positions
        params_dict (Dict[str, Union[int, List[str]]]): Dictionary of configuration parameters
        methode (str): Cost calculation method to use ('linéaire', 'carré', or 'exp')
        file_name (str | None): Optional name of the input file for saving results

    Returns:
        Tuple containing:
            - voeux_df (pd.DataFrame): Updated DataFrame with assignment results
            - proportions_voeux (plt.Figure): Figure showing wish fulfillment distribution
            - proportion_top_3 (float): Percentage of auditors assigned to one of their top 3 wishes
            - proportion_top_4 (float): Percentage of auditors assigned to one of their top 4 wishes
            - moyenne_globale (float): Average wish number at which auditors are assigned
    """
    voeux_df = original_voeux_df.copy()
    indice_vers_ville = []
    i = 0
    for ville in villes.values():
        for _ in range(ville.capacite):
            indice_vers_ville.append(ville.nom)
            ville.colonnes.append(i)
            i = i + 1

    repartition_df = voeux_df.sample(frac=1, random_state=seed).reset_index()

    matrice_couts = creer_matrice_couts(nb_auditeurs, nb_postes, repartition_df, villes, params_dict, methode)
    row_ind, col_ind = optimize.linear_sum_assignment(matrice_couts)

    voeux_df['assignation'] = ''
    voeux_df['voeu_realise'] = np.nan
    for index in row_ind:
        id_auditeur = repartition_df.loc[index, 'id_auditeur']
        assignation = indice_vers_ville[col_ind[index]]
        voeux_df.loc[id_auditeur, 'voeu_realise'] = recuperer_num_voeu(voeux_df.loc[id_auditeur][:-2].values, assignation)
        voeux_df.loc[id_auditeur, 'assignation'] = assignation
    voeux_df['voeu_realise'] = voeux_df['voeu_realise'].astype(int)
    voeux_df.to_csv(os.path.join(RESULTS_PATH, f'resultats_{file_name[:-4]}_{methode}.csv'))
    proportions = voeux_df['voeu_realise'].value_counts().sort_index()

    proportions_voeux = plt.figure()
    proportions.plot.pie(autopct='%1.1f%%', ylabel='', title=f"Méthode utilisée: {methode}")
    proportion_top_3 = 100 * proportions.loc[1:3].sum() / proportions.sum()
    proportion_top_4 = 100 * proportions.loc[1:4].sum() / proportions.sum()
    moyenne_globale = voeux_df['voeu_realise'].mean()
    return voeux_df, proportions_voeux, proportion_top_3, proportion_top_4, moyenne_globale