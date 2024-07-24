import numpy as np
import os
import streamlit as st
import matplotlib.pyplot as plt
from scipy import optimize
from utils import *
from villes import Ville

seed = 42
RESULTS_PATH = "./resultats/"

def verification_et_analyse_des_voeux(postes_df, voeux_df, params_dict, cas_part_df = None):
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

    if cas_part_df is not None:
        st.write("\nTraitement des cas particuliers:")
        for index, row in cas_part_df.iterrows():
            aud = row['id_auditeur']
            v_max = row['v_max']
            st.write(
                f"L'auditeur {aud} doit être placé sur ses {v_max} premiers voeux."
            )
            voeux_df.loc[aud, [f'v_{i}' for i in range(v_max+1, voeux_df.shape[1]+1)]] = np.nan

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


def executer_la_repartition(villes, original_voeux_df, nb_auditeurs, nb_postes, params_dict, methode, file_name=None):
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