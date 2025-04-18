"""
Ce fichier implémente l'objet 'Ville' dont une instance représente un TJ.

Auteur: Vincent O'Luasa
Contact: vincent.oluasa@gmail.com
Date d'écriture: Juillet 2024

Cette classe est basée sur le travail de Paul Simon, AdJ. 2019
Contact: paul.dc.simon@gmail.com
"""


class Ville:
    def __init__(self, numero, nom, places):
        self.num = numero
        self.nom = nom
        self.capacite = places
        self.colonnes = list()
