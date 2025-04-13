"""
Ce fichier implémente 2 fonctions:
    - verification_et_analyse_des_voeux: En charge de la vérification et d'analyse des voeux,
    - executer_la_repartition: En charge de la répartition des auditeurs.

Auteur: Vincent O'Luasa
Contact: vincent.oluasa@gmail.com
Date d'écriture: Juillet 2024

Ces fonctions sont basées sur le travail de Paul Simon, AdJ. 2019
Contact: paul.dc.simon@gmail.com
"""

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


def verification_et_analyse_des_voeux(
    postes_df: pd.DataFrame, voeux_df: pd.DataFrame, params_dict: Dict[str, Any]
) -> Tuple[
    Dict[str, Ville],
    pd.DataFrame,
    pd.DataFrame,
    int,
    int,
    plt.Figure,
    plt.Figure,
    plt.Figure,
]:
    """Analyse et vérifie les voeux des auditeurs et prépare les données pour la répartition.

    Cette fonction effectue plusieurs tâches principales :
    1. Vérifie la validité des voeux par rapport aux contraintes
    2. Analyse la distribution des voeux
    3. Génère des visualisations des données
    4. Prépare les données pour le processus de répartition

    Args:
        postes_df (pd.DataFrame): DataFrame contenant les informations des TJs (Tribunaux Judiciaires) incluant :
            - Ville : Nom de la ville
            - Postes : Nombre de postes disponibles
            - Couleur : Classification par couleur de la ville
        voeux_df (pd.DataFrame): DataFrame contenant les voeux des auditeurs avec les colonnes :
            - id_auditeur : Identifiant de l'auditeur
            - v_1, v_2, etc. : Colonnes contenant les voeux
        params_dict (Dict[str, Any]): Dictionnaire contenant les paramètres de configuration :
            - Voeux max : Nombre maximum de voeux par auditeur
            - Noires max : Nombre maximum de villes noires
            - Noires ou rouges max : Nombre maximum de villes rouges ou noires
            - Vertes min : Nombre minimum de villes vertes
            - Methodes : Liste des méthodes de calcul des coûts
            - Penalite : Pénalité par défaut pour les affectations

    Returns:
        Tuple contenant :
            - villes (Dict[str, Ville]) : Dictionnaire d'objets Ville représentant chaque TJ
            - postes_df (pd.DataFrame) : DataFrame des postes mise à jour avec l'analyse de la distribution des voeux
            - voeux_df (pd.DataFrame) : DataFrame des voeux mise à jour après vérification
            - nb_postes (int) : Nombre total de postes disponibles
            - nb_auditeurs (int) : Nombre total d'auditeurs
            - top_30_demandes (plt.Figure) : Graphique montrant les 30 villes les plus demandées
            - top_30_voeux1 (plt.Figure) : Graphique montrant les 30 villes les plus demandées en premier voeu
            - taux_assignation (plt.Figure) : Graphique montrant l'analyse des taux d'affectation
    """
    voeux = params_dict["Voeux"]
    nb_postes = postes_df["Postes"].sum()

    villes = {}  # Dictionnaire de Villes qui contient toutes les villes
    for index, row in postes_df.iterrows():
        if row["Postes"] > 0:
            villes[row["Ville"]] = Ville(index, row["Ville"], row["Postes"])
        else:
            st.write("Ville ignorée (aucun poste) :", row["Ville"])

    st.write(f"Il y a {nb_postes} postes disponibles dans {len(postes_df)} villes.")
    st.divider()

    # Vérification des voeux
    st.write(
        "Critères de validation des voeux:\n"
        + "\n- Nombre de voeux suffisant,"
        + "\n- Existence de chaque ville souhaitée,"
        + "\n- Unicité des voeux,"
        + "\n- Respect des règles de couleur."
    )

    erreurs, valides, trop_de_voeux = verification_voeux(
        voeux_df, postes_df, params_dict
    )

    st.write(f"Voeux valides: {valides} | Voeux invalides: {erreurs}.")
    if trop_de_voeux > 0:
        st.write(
            f"{trop_de_voeux} auditeurs sur {valides} ont formulé plus de {voeux} voeux"
        )
    st.divider()

    nb_auditeurs = len(voeux_df)

    st.write(f"Il y a {nb_auditeurs} auditeurs à répartir sur {nb_postes} postes.\n")
    marge = nb_postes - nb_auditeurs

    # Traitement des cas particuliers
    voeux_df.set_index("id_auditeur", inplace=True)

    # Calcul du nombre de villes n'ayant été demandées par personne :
    postes_df, nb_postes_non_demandes = distribution_des_voeux(
        villes, voeux_df, postes_df, voeux
    )
    postes_df.to_csv(os.path.join(RESULTS_PATH, "distribution_voeux.csv"), index=False)

    if (nb_postes_non_demandes > marge) or (erreurs > 0):
        st.write(
            f"Il y aura donc au moins {max(nb_postes_non_demandes - marge, erreurs)} auditeurs placés hors de leurs voeux (dont {erreurs} pour cause de voeux invalides)."
        )

    top_30_demandes, ax1 = plt.subplots(1, 1)
    top_30_voeux1, ax2 = plt.subplots(1, 1)
    ax_demandes = (
        postes_df.sort_values(by="total_demandes", ascending=False)
        .set_index("Ville")
        .head(30)[["total_demandes", "Postes"]]
        .plot.bar(figsize=(10, 5), ax=ax1, xlabel="")
    )
    ax_demandes.bar_label(ax_demandes.containers[0])
    ax_voeux = (
        postes_df.sort_values(by="nombre_voeux_1", ascending=False)
        .set_index("Ville")
        .head(30)[["nombre_voeux_1", "Postes"]]
        .plot.bar(figsize=(10, 5), ax=ax2, xlabel="")
    )
    ax_voeux.bar_label(ax_voeux.containers[0])
    ax1.legend(["Nombre de voeux", "Nombre de postes"])
    ax2.legend(["Nombre de 1er voeux", "Nombre de postes"])

    # Taux d'assignation
    assignment_rates = {}
    for nb_voeux in range(1, voeux + 1):
        cols = [f"nombre_voeux_{i}" for i in range(1, nb_voeux + 1)]
        rate = min(
            100
            * postes_df.dropna(how="all", subset=cols)["Postes"].sum()
            / nb_auditeurs,
            100,
        )
        assignment_rates[nb_voeux] = rate
    taux_assignation, ax_rates = plt.subplots()
    bar_container = ax_rates.bar(
        range(len(assignment_rates)), list(assignment_rates.values()), align="center"
    )
    ax_rates.bar_label(bar_container, fmt="{:,.1f}%")
    plt.xticks(range(len(assignment_rates)), list(assignment_rates.keys()))
    plt.xlabel("Numéro du voeu (N)")
    plt.ylabel("Taux d'assignation (%)")
    plt.ylim(60, 103)

    return (
        villes,
        postes_df,
        voeux_df,
        nb_postes,
        nb_auditeurs,
        top_30_demandes,
        top_30_voeux1,
        taux_assignation,
    )


def executer_la_repartition(
    villes: Dict[str, Ville],
    original_voeux_df: pd.DataFrame,
    nb_auditeurs: int,
    nb_postes: int,
    params_dict: Dict[str, Union[int, List[str]]],
    methode: str,
    file_name: str | None = None,
) -> Tuple[pd.DataFrame, plt.Figure, float, float, float]:
    """Exécute la répartition des auditeurs sur les postes en utilisant la méthode spécifiée.

    Cette fonction :
    1. Crée une matrice de coûts basée sur les voeux et les contraintes
    2. Utilise l'algo scipy.optimize.linear_sum_assignmentpour trouver la répartition optimale
    3. Génère les résultats et les visualisations
    4. Sauvegarde les résultats en CSV

    Args:
        villes (Dict[str, Ville]) : Dictionnaire d'objets Ville représentant chaque TJ
        original_voeux_df (pd.DataFrame) : DataFrame contenant les voeux des auditeurs
        nb_auditeurs (int) : Nombre total d'auditeurs à répartir
        nb_postes (int) : Nombre total de postes disponibles
        params_dict (Dict[str, Union[int, List[str]]]) : Dictionnaire des paramètres de configuration
        methode (str) : Méthode de calcul des coûts à utiliser ('linéaire', 'carré', ou 'exp')
        file_name (str | None) : Nom optionnel du fichier d'entrée pour la sauvegarde des résultats

    Returns:
        Tuple contenant :
            - voeux_df (pd.DataFrame) : DataFrame mise à jour avec les résultats d'affectation
            - proportions_voeux (plt.Figure) : Figure montrant la distribution des affectations
            - proportion_top_3 (float) : Pourcentage d'auditeurs affectés à l'un de leurs 3 premiers voeux
            - proportion_top_4 (float) : Pourcentage d'auditeurs affectés à l'un de leurs 4 premiers voeux
            - moyenne_globale (float) : Numéro moyen du voeu auquel les auditeurs sont affectés
    """
    # Création d'une copie pour éviter de modifier les données originales
    voeux_df = original_voeux_df.copy()

    # Construction d'une liste qui mappe chaque poste à sa ville
    # Cette liste est utilisée pour convertir les indices de la matrice en noms de villes
    indice_vers_ville = []
    i = 0
    for ville in villes.values():
        for _ in range(ville.capacite):
            indice_vers_ville.append(ville.nom)
            ville.colonnes.append(
                i
            )  # Stockage des indices de colonnes pour chaque ville
            i = i + 1

    # Mélange aléatoire des auditeurs pour éviter les biais dans l'affectation
    repartition_df = voeux_df.sample(frac=1, random_state=seed).reset_index()

    # Création de la matrice de coûts et résolution du problème d'affectation
    matrice_couts = creer_matrice_couts(
        nb_auditeurs, nb_postes, repartition_df, villes, params_dict, methode
    )
    row_ind, col_ind = optimize.linear_sum_assignment(matrice_couts)

    # Initialisation des colonnes pour stocker les résultats
    voeux_df["assignation"] = ""
    voeux_df["voeu_realise"] = np.nan

    # Affectation des postes aux auditeurs en utilisant les résultats de l'algorithme
    for index in row_ind:
        id_auditeur = repartition_df.loc[index, "id_auditeur"]
        assignation = indice_vers_ville[col_ind[index]]
        # Récupération du numéro du voeu réalisé (1er, 2ème, etc.)
        voeux_df.loc[id_auditeur, "voeu_realise"] = recuperer_num_voeu(
            voeux_df.loc[id_auditeur][:-2].values, assignation
        )
        voeux_df.loc[id_auditeur, "assignation"] = assignation

    # Conversion des résultats en int et sauvegarde
    voeux_df["voeu_realise"] = voeux_df["voeu_realise"].astype(int)
    voeux_df.to_csv(
        os.path.join(RESULTS_PATH, f"resultats_{file_name[:-4]}_{methode}.csv")
    )

    # Calcul des statistiques sur les affectations
    proportions = voeux_df["voeu_realise"].value_counts().sort_index()

    # Création du graphique en camembert des affectations
    proportions_voeux = plt.figure()
    proportions.plot.pie(
        autopct="%1.1f%%", ylabel="", title=f"Méthode utilisée: {methode}"
    )

    # Calcul des indicateurs de performance
    proportion_top_3 = (
        100 * proportions.loc[1:3].sum() / proportions.sum()
    )  # % affectés dans leurs 3 premiers voeux
    proportion_top_4 = (
        100 * proportions.loc[1:4].sum() / proportions.sum()
    )  # % affectés dans leurs 4 premiers voeux
    moyenne_globale = voeux_df[
        "voeu_realise"
    ].mean()  # Moyenne du rang des voeux réalisés

    return (
        voeux_df,
        proportions_voeux,
        proportion_top_3,
        proportion_top_4,
        moyenne_globale,
    )
