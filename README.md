# Répartition des Auditeurs

Une application web pour la répartition optimale des auditeurs de justice sur les différents tribunaux judiciaires, en tenant compte de leurs voeux et des contraintes spécifiques.

## Description

Cette application permet de :
- Charger les données des postes disponibles et des voeux des auditeurs
- Vérifier la validité des voeux selon différentes contraintes
- Analyser la distribution des voeux
- Effectuer une répartition optimale selon différentes méthodes de calcul
- Visualiser les résultats de la répartition

## Installation

1. Clonez le dépôt :
```bash
git clone [URL_DU_REPO]
cd repartition_enm
```

2. Créez un environnement virtuel et activez-le :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Structure du Projet

```
repartition_enm/
├── app/
│   ├── app.py              # Application Streamlit principale
│   ├── repartition.py      # Fonctions de répartition et d'analyse
│   ├── utils.py            # Fonctions utilitaires
│   └── villes.py           # Classe Ville
├── config/
│   └── parametres.json     # Fichier de configuration
├── logs/                   # Dossier pour les logs
├── requirements.txt        # Dépendances du projet
└── README.md              # Documentation
```

## Utilisation

1. Lancez l'application :
```bash
streamlit run app/app.py
```

2. Dans l'interface web :
   - Chargez le fichier des postes (CSV)
   - Chargez le fichier des voeux (CSV)
   - Configurez les paramètres dans la barre latérale :
     - Nombre de voeux
     - Contraintes sur les villes noires/rouges/vertes
     - Méthode de calcul des coûts
     - Option "Voeux libres" pour relâcher les contraintes de couleurs
   - Visualisez les résultats et les analyses

## Fonctionnalités

### Vérification des Voeux
- Vérification de l'existence des villes souhaitées
- Contrôle du nombre de voeux
- Vérification des contraintes de couleurs (villes noires, rouges, vertes)
- Détection des doublons

### Analyse
- Distribution des voeux par ville
- Taux d'assignation potentiel
- Top 30 des villes les plus demandées
- Analyse des premiers voeux

### Répartition
- Trois méthodes de calcul des coûts :
  - Linéaire
  - Carré
  - Exponentielle
- Optimisation de l'affectation
- Visualisation des résultats

## Format des Fichiers d'Entrée
⚠️ **Important** : Il est impératif de respecter le nom des colonnes des fichiers.

### Fichier des Postes (CSV)
La colonne "Postes" indique le nombre de postes disponibles dans le TJ associé
```csv
Ville,Postes,Couleur
Paris,10,rouge
Lyon,5,noir
...
```

### Fichier des Voeux (CSV)
La colonne "id_auditeur" indique l'identifiant d'un auditeur, ce qui peut être un numéro ou un nom-prenom.
```csv
id_auditeur,v_1,v_2,v_3,...
1,Paris,Lyon,Marseille,...
2,Lyon,Paris,Bordeaux,...
...
```

## Auteurs

- Vincent O'Luasa
- Contact : vincent.oluasa@gmail.com

- Ce projet est basé sur le travail de Paul Simon, AdJ. 2019
- Contact : paul.dc.simon@gmail.com 