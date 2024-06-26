import pandas as pd
import json
import numpy as np
import os
from scipy import optimize
from utils import *
from villes import Ville

FILES_PATH = "config/"
RESULTS_PATH = "resultats/"
seed = 42

print("Affectation des auditeurs de justice en stage juridictionnel", end="\n\n")

########################################################################################################################
########################################################################################################################

# Paramètres de la répartition
with open(os.path.join(FILES_PATH, "parametres_refactor.json"), "r") as f:
    params_dict = json.load(f)
voeux_max = params_dict["Voeux max"]

print("Paramètres de la répartition:", params_dict, end="\n\n")

# Table des postes
postes_df = pd.read_csv(os.path.join(FILES_PATH, "postes_refactor.csv"))
nb_postes = postes_df["Postes"].sum()
print("Recensement des postes :")
villes = {}  # dictionnaire de Villes qui contient toutes les villes
for index, row in postes_df.iterrows():
    if row["Postes"] > 0:
        villes[row["Ville"]] = Ville(index, row["Ville"], row["Postes"])
    else:
        print("Ville ignorée (aucun poste) :", row["Ville"])
print(
    "Il y a " + str(nb_postes) + " postes disponibles dans " + str(len(postes_df)) + " villes.", end="\n\n",
)

next()
########################################################################################################################
########################################################################################################################

# Vérification des voeux
print("Validation des voeux  de chaque auditeur:")
print("\t- Nombre de voeux suffisant,")
print("\t- Existence de chaque ville,")
print("\t- Absence de doublons,")
print("\t- Respect des règles de couleur.", end="\n\n")

voeux_df = pd.read_csv(os.path.join(FILES_PATH, "sondage_refactor.csv"))
erreurs, valides, trop_de_voeux = verification_voeux(voeux_df, postes_df, params_dict)

print(
    "\nVoeux validés : " + str(valides) + " auditeurs ; Voeux invalides : " + str(erreurs) + " auditeurs."
)
print(
    str(trop_de_voeux) + " auditeurs sur " + str(valides) + " ont formulé plus de " + str(voeux_max) + " voeux"
)
nb_auditeurs = len(voeux_df)

print(
    "Il y a " + str(nb_auditeurs) + " auditeurs à répartir sur " + str(nb_postes) + " postes.\n"
)
marge = nb_postes - nb_auditeurs
next()
########################################################################################################################
########################################################################################################################

# Traitement des cas particuliers
voeux_df.set_index('id_auditeur', inplace=True)

try:
	cas_part_df = pd.read_csv(os.path.join(FILES_PATH, 'cas_particuliers.csv'))
	print("\nTraitement des cas particuliers:")
	for index, row in cas_part_df.iterrows():
		aud = row['id_auditeur']
		v_max = row['v_max']
		print(
			"L'auditeur " + str(aud) + " doit être placé sur ses " + str(v_max) + " premiers voeux."
		)
		voeux_df.loc[aud, [f'v_{i}' for i in range(v_max+1, voeux_df.shape[1]+1)]] = np.nan
except Exception as e:
    print("Erreur dans la lecture des cas particuliers: (Ignorer l'erreur s'il n'y a pas de cas particuliers et donc pas de fichier cas_particuliers.csv)")
    print(e)
    pass
########################################################################################################################
########################################################################################################################

# Calcul du nombre de villes n'ayant été demandées par personne :
postes_df, nb_postes_non_demandes = distribution_des_voeux(villes, voeux_df, postes_df, voeux_max)
postes_df.to_csv(os.path.join(RESULTS_PATH, 'distribution_voeux.csv'), index=False)

print("Taille de la marge de postes:", marge, end='\n\n')
if (nb_postes_non_demandes > marge) or (erreurs > 0):
    print(
        "Il y aura forcément au moins " + str(max(nb_postes_non_demandes - marge, erreurs)) + " auditeurs placés hors de leurs voeux :(\n(dont " + str(erreurs) + " pour cause de voeux invalides)."
    )

print("\nFIN DU TRAITEMENT DES DONNEES\n")
next()
print(
    "********************************************************************************"
)
########################################################################################################################
########################################################################################################################
print("\nDÉBUT DE LA RÉPARTITION\n")

indice_vers_ville = []
i = 0
for ville in villes.values():
    for foo in range(ville.capacite):
        indice_vers_ville.append(ville.nom)
        ville.colonnes.append(i)
        i = i + 1

repartition_df = voeux_df.sample(frac=1, random_state=seed).reset_index()

penalite = 1e9
matrice_couts = creer_matrice_couts(nb_auditeurs, nb_postes, repartition_df, villes, params_dict, penalite)
row_ind, col_ind = optimize.linear_sum_assignment(matrice_couts)

voeux_df['assignation'] = ''
voeux_df['voeu_realise'] = np.nan
for index in row_ind:
    id_auditeur = repartition_df.loc[index, 'id_auditeur']
    assignation = indice_vers_ville[col_ind[index]]
    voeux_df.loc[id_auditeur, 'voeu_realise'] = recuperer_num_voeu(voeux_df.loc[id_auditeur][:-2].values, assignation)
    voeux_df.loc[id_auditeur, 'assignation'] = assignation
voeux_df['voeu_realise'] = voeux_df['voeu_realise'].astype(int)
voeux_df.to_csv(os.path.join(RESULTS_PATH, 'resultats.csv'))

print("FIN DE LA RÉPARTITION", end='\n\n')
next()
print(
    "********************************************************************************"
)
########################################################################################################################
########################################################################################################################