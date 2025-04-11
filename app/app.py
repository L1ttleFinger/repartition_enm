'''
Ce fichier implémente la webapp en utilisant la librairie streamlit (https://docs.streamlit.io/develop/api-reference)

Auteur: Vincent O'Luasa
Contact: vincent.oluasa@gmail.com
Date d'écriture: Juillet 2024
'''

import streamlit as st
import json
import os
import pandas as pd
from repartition import *

# Configuration path for parameter files
FILES_PATH = "./config/"

st.title("Stage Juridictionnel")

# Load and initialize parameters from JSON file
with open(os.path.join(FILES_PATH, "parametres.json"), "r") as f:
    params_dict = json.load(f)
# Extract key parameters for easier access
voeux_max = params_dict['Voeux max']  # Maximum number of wishes per auditor
noires_max = params_dict['Noires max']  # Maximum number of black cities
noires_ou_rouges_max = params_dict['Noires ou rouges max']  # Maximum number of black or red cities
vertes_min = params_dict['Vertes min']  # Minimum number of green cities
methode = params_dict['Methodes']  # Method for cost calculation
penalite = params_dict['Penalite']  # Default penalty for post assignments
methods = ['linéaire', 'carré', 'exp']  # Available cost calculation methods

# File upload section for post and wish data
uploaded = False
postes, voeux = st.columns(2)
with postes:
    st.subheader('Postes')
    postes_file = st.file_uploader('Uploader ici le fichier contenant les postes et couleurs')
with voeux:
    st.subheader('Voeux')
    voeux_file = st.file_uploader('Uploader ici le fichier contenant les voeux des auditeurs')
uploaded = postes_file and voeux_file

# Sidebar for parameter configuration
with st.sidebar:
    st.header("Paramètres de la répartition")
    # Interactive widgets for parameter adjustment
    params_dict['Voeux max'] = st.number_input('Nombre de voeux maximum', min_value=1, value=voeux_max)
    params_dict['Noires max'] = st.number_input('Nombre de villes noires maximum', min_value=0, value=noires_max)
    params_dict['Noires ou rouges max'] = st.number_input('Nombre de villes rouges ou noires maximum', min_value=params_dict['Noires max'], value=max(params_dict['Noires max'], noires_ou_rouges_max))
    params_dict['Vertes min'] = st.number_input('Nombre de villes vertes minimum', min_value=0, value=vertes_min)
    params_dict['Penalite'] = st.number_input('Penalite a appliquer par défaut aux postes', min_value=1000000, value=penalite, step=1000)
    params_dict['Methodes'] = st.multiselect(
                                "Méthode de calcul des coûts",
                                methods,
                                default=methode,
                                placeholder="Selectionner la méthode de calcul des coûts",
                            )

# Main content area - only shown when files are uploaded
if not uploaded:
    st.subheader('Veuillez uploader les fichiers demandés pour démarrer la répartition.')
else:
    st.write('\n')
    st.header('Répartition des auditeurs')
    # Load and display the uploaded data
    postes_df = pd.read_csv(postes_file)
    voeux_df = pd.read_csv(voeux_file)
    
    # Display data in tabs
    postes_tab, voeux_tab = st.tabs(["Postes", "Voeux"])
    with postes_tab:
        st.subheader("Postes disponibles:")
        st.dataframe(postes_df)
    with voeux_tab:
        st.subheader("Voeux des auditeurs:")
        st.dataframe(voeux_df.set_index('id_auditeur'))

    # Analysis section with multiple tabs
    st.subheader('Vérification et analyse des voeux:')
    recap_tab, distribution_tab, taux_tab, graph_tab = st.tabs(["Récapitulatif de l'analyse", "Distribution des voeux", "Taux d'assignation", "Graphiques des plus fortes demandes"])
    
    # Perform wish verification and analysis
    with recap_tab:
        villes, postes_df, voeux_df, nb_postes, nb_auditeurs, top_30_demandes, top_30_voeux1, taux_assignation = verification_et_analyse_des_voeux(postes_df, voeux_df, params_dict)
    
    with distribution_tab:
        st.dataframe(postes_df)
    
    with taux_tab:
        st.write("Taux d'assignation: pourcentage de la promotion pouvant être assigné à l'un de ses voeux.")
        st.write("Le graphique ci-dessous présente les taux d'assignation maximaux que l'on peut espérer obtenir en ne prenant en compte que les n premiers voeux.")
        st.write("Pour avoir le taux d'assignation réel il faut lancer la répartition sur les n premiers voeux.")
        st.pyplot(taux_assignation)
    
    with graph_tab:
        st.subheader("Top 30 des villes les plus demandées:")
        st.pyplot(top_30_demandes)
        st.pyplot(top_30_voeux1)

    # Execute distribution for each selected method
    for methode in params_dict['Methodes']:
        st.divider()
        st.subheader(f"Répartition pour la méthode {methode}:")
        # Execute the distribution and get results
        res_voeux_df, proportions_voeux, proportion_top_3, proportion_top_4, moyenne_globale = executer_la_repartition(villes, voeux_df, nb_auditeurs, nb_postes, params_dict, methode, file_name = voeux_file.name)
        
        # Display results in tabs
        graph_repartition_tab, resultats_tab = st.tabs(["Graphiques", "Résultats"])
        with graph_repartition_tab:
            st.write("Proportion des affectations en fonction du voeu:")
            chart, moyenne = st.columns(2)
            with chart:
                st.pyplot(proportions_voeux)
            with moyenne:
                st.write(f"- {proportion_top_3:.1f}% de la promo est affectée à l'un de ses 3 premiers voeux.")
                st.write(f"- {proportion_top_4:.1f}% de la promo est affectée à l'un de ses 4 premiers voeux.")
                st.write(f"- Les auditeurs sont affectés en moyenne à leur {moyenne_globale:.2f}ème voeu.")
        with resultats_tab:
            st.write("Affectations des auditeurs:")
            resultats = st.dataframe(res_voeux_df[['assignation', 'voeu_realise']])