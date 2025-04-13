"""
Ce fichier implémente la webapp en utilisant la librairie streamlit (https://docs.streamlit.io/develop/api-reference)

Auteur: Vincent O'Luasa
Contact: vincent.oluasa@gmail.com
Date d'écriture: Juillet 2024
"""

import streamlit as st
import json
import os
import pandas as pd
from repartition import *

# Path du fichier configuration
CONFIG_PATH = "./config/"

st.title("Stage Juridictionnel")

# Chargement et initialisation des paramètres depuis le fichier JSON
with open(os.path.join(CONFIG_PATH, "parametres.json"), "r") as f:
    params_dict = json.load(f)
# Extraction des paramètres
num_voeux = params_dict["Voeux"]  # Nombre maximum de voeux par auditeur
noires_max = params_dict["Noires max"]  # Nombre maximum de villes noires
noires_ou_rouges_max = params_dict[
    "Noires ou rouges max"
]  # Nombre maximum de villes rouges ou noires
vertes_min = params_dict["Vertes min"]  # Nombre minimum de villes vertes
methode = params_dict["Methodes"]  # Méthode pour le calcul des coûts
penalite = params_dict["Penalite"]  # Pénalité par défaut pour les affectations
methods = ["linéaire", "carré", "exp"]  # Méthodes de calcul des coûts disponibles

# Section d'upload des fichiers pour les données des postes et des voeux
uploaded = False
postes, voeux = st.columns(2)
with postes:
    st.subheader("Postes")
    postes_file = st.file_uploader(
        "Uploader ici le fichier contenant les postes et couleurs"
    )
with voeux:
    st.subheader("Voeux")
    voeux_file = st.file_uploader(
        "Uploader ici le fichier contenant les voeux des auditeurs"
    )
uploaded = postes_file and voeux_file

# Barre latérale pour la configuration des paramètres
with st.sidebar:
    st.header("Paramètres de la répartition")
    # Widget indicant si les voeux sont faits sans contraintes de couleurs ou non
    voeux_libres = st.toggle("Voeux libres", value=False)
    # Widgets interactifs pour l'ajustement des paramètres
    params_dict["Voeux"] = st.number_input(
        "Nombre de voeux", min_value=1, value=num_voeux, disabled=voeux_libres
    )
    params_dict["Noires max"] = st.number_input(
        "Nombre de villes noires maximum",
        min_value=0,
        value=noires_max,
        disabled=voeux_libres,
    )
    params_dict["Noires ou rouges max"] = st.number_input(
        "Nombre de villes rouges ou noires maximum",
        min_value=params_dict["Noires max"],
        value=max(params_dict["Noires max"], noires_ou_rouges_max),
        disabled=voeux_libres,
    )
    params_dict["Vertes min"] = st.number_input(
        "Nombre de villes vertes minimum",
        min_value=0,
        value=vertes_min,
        disabled=voeux_libres,
    )
    params_dict["Penalite"] = st.number_input(
        "Penalite a appliquer par défaut aux postes",
        min_value=1000000,
        value=penalite,
        step=1000,
    )
    params_dict["Methodes"] = st.multiselect(
        "Méthode de calcul des coûts",
        methods,
        default=methode,
        placeholder="Selectionner la méthode de calcul des coûts",
    )

# Zone de contenu principale - affichée uniquement lorsque les fichiers sont téléchargés
if not uploaded:
    st.subheader(
        "Veuillez uploader les fichiers demandés pour démarrer la répartition."
    )
else:
    st.write("\n")
    st.header("Répartition des auditeurs")
    # Chargement et affichage des données téléchargées
    postes_df = pd.read_csv(postes_file)
    voeux_df = pd.read_csv(voeux_file)

    if voeux_libres:
        nb_voeux = len([col for col in voeux_df.columns if col.startswith("v_")])
        params_dict["Voeux"] = nb_voeux
        params_dict["Noires max"] = nb_voeux
        params_dict["Noires ou rouges max"] = nb_voeux
        params_dict["Vertes min"] = 0

    # Affichage des données dans des onglets
    postes_tab, voeux_tab = st.tabs(["Postes", "Voeux"])
    with postes_tab:
        st.subheader("Postes disponibles:")
        st.dataframe(postes_df)
    with voeux_tab:
        st.subheader("Voeux des auditeurs:")
        st.dataframe(voeux_df.set_index("id_auditeur"))

    # Section d'analyse avec plusieurs onglets
    st.subheader("Vérification et analyse des voeux:")
    recap_tab, distribution_tab, taux_tab, graph_tab = st.tabs(
        [
            "Récapitulatif de l'analyse",
            "Distribution des voeux",
            "Taux d'assignation",
            "Graphiques des plus fortes demandes",
        ]
    )

    # Exécution de la vérification et de l'analyse des voeux
    with recap_tab:
        (
            villes,
            postes_df,
            voeux_df,
            nb_postes,
            nb_auditeurs,
            top_30_demandes,
            top_30_voeux1,
            taux_assignation,
        ) = verification_et_analyse_des_voeux(postes_df, voeux_df, params_dict)

    with distribution_tab:
        st.dataframe(postes_df)

    with taux_tab:
        st.write(
            "*Taux d'assignation: pourcentage de la promotion pouvant être assigné à l'un de ses voeux.*"
        )
        st.write(
            "Le graphique ci-dessous présente les **taux d'assignation maximaux** que l'on peut espérer "
            "obtenir en ne prenant en compte que les N premiers voeux. Il a pour objectif d'indiquer jusqu'à quel voeu "
            "on peut espérer restreindre l'affectation des auditeurs.\n\n"
            "Un taux d'assignation a 80% **ne signifie pas** que 80% des auditeurs seront affectés à l'un de leurs N premiers voeux, "
            "mais que c'est une **possibilité**. En revanche, cela signifie **qu'au moins 20% des "
            "auditeurs** seront affectés à un TJ **en dehors de leurs N premiers choix**."
        )
        st.write(
            "Pour avoir le taux d'assignation réel il faut lancer la répartition sur les N premiers voeux."
        )
        st.pyplot(taux_assignation)

    with graph_tab:
        st.subheader("Top 30 des villes les plus demandées:")
        st.pyplot(top_30_demandes)
        st.pyplot(top_30_voeux1)

    # Exécution de la répartition pour chaque méthode sélectionnée
    for methode in params_dict["Methodes"]:
        st.divider()
        st.subheader(f"Répartition pour la méthode {methode}:")
        # Exécution de la répartition et récupération des résultats
        (
            res_voeux_df,
            proportions_voeux,
            proportion_top_3,
            proportion_top_4,
            moyenne_globale,
        ) = executer_la_repartition(
            villes,
            voeux_df,
            nb_auditeurs,
            nb_postes,
            params_dict,
            methode,
            file_name=voeux_file.name,
        )

        # Affichage des résultats dans des onglets
        graph_repartition_tab, resultats_tab = st.tabs(["Graphiques", "Résultats"])
        with graph_repartition_tab:
            st.write("Proportion des affectations en fonction du voeu:")
            chart, moyenne = st.columns(2)
            with chart:
                st.pyplot(proportions_voeux)
            with moyenne:
                st.write(
                    f"- {proportion_top_3:.1f}% de la promo est affectée à l'un de ses 3 premiers voeux."
                )
                st.write(
                    f"- {proportion_top_4:.1f}% de la promo est affectée à l'un de ses 4 premiers voeux."
                )
                st.write(
                    f"- Les auditeurs sont affectés en moyenne à leur {moyenne_globale:.2f}ème voeu."
                )
        with resultats_tab:
            st.write("Affectations des auditeurs:")
            resultats = st.dataframe(res_voeux_df[["assignation", "voeu_realise"]])
