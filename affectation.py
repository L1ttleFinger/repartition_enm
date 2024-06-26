import csv
from datetime import timedelta, datetime
import numpy as np
from scipy import optimize
import random
import png
import matplotlib.pyplot as plt
import time


#########################################
#########################################
##                                     ##
##         FONCTIONS ETAPE 1           ##
##                                     ##
#########################################
#########################################

class Auditeur:
	def __init__(self, login):
		self.nom = login
		self.mdp = ""
		self.date_voeux = datetime.fromordinal(1)
		self.voeux=list()


def str_date_to_datetime(s):
	dt=s.split(" - ")
	d=dt[0].split("/")
	t=dt[1].split(":")
	result=datetime(int(d[2]),int(d[1]),int(d[0]),int(t[0]),int(t[1]))
	return(result)

def verifier_login_mdp(login,mdp,table):
	return (table[login]==mdp)

def verifier_unicite_voeux(l):
	return (len(set(l))==len(l))

def villes_existantes(l):
	l_villes = villes.keys()
	ok = True
	for v in l:
		if not(v in l_villes):
			ok = False
	return(ok)


def pb_villes_existantes(l):
	l_villes = villes.keys()
	ok = True
	for v in l:
		if not(v in l_villes):
			return(v)
	return("")

def compte_rouge(l):
	n = 0
	for x in l:
		if (x in villes_rouges):
			n=n+1
	return(n)	

def compte_noir(l):
	n = 0
	for x in l:
		if (x in villes_noires):
			n=n+1
	return(n)

def compte_vert(l):
	n = 0
	for x in l:
		if (x in villes_vertes):
			n=n+1
	return(n)

def strfy(l):
	s=l[0][:3]
	for x in l[1:]:
		s=s+"\t"+x[:3]
	return(s)

def nettoie(v):
	s=v.split('//')[0].strip()
	return(s)
	

def next():
	input("Appuyer sur ENTRÉE pour continuer...")
	print()
	time.sleep(0.1)

#########################################
#########################################
##                                     ##
##         FONCTIONS ETAPE 2           ##
##                                     ##
#########################################
#########################################

class Ville:
	def __init__(self,numero,nom,places):
		self.num=numero
		self.nom=nom
		self.capacite=places
		self.colonnes=list()






#########################################
#########################################
##                                     ##
##         FONCTIONS ETAPE 3           ##
##                                     ##
#########################################
#########################################






#########################################
#########################################
##                                     ##
##              MAIN                   ##
##                                     ##
#########################################
#########################################

f=open("splash.txt")
print(f.read())
f.close()

nb_voeux_max = 50 # valeur arbitraire, à modifier éventuellement

# Paramètres de la répartition
tot_voeux = 6
noires_max = 2
rougesplusnoires_max = 4
vertes_min = 0

time.sleep(.5)
print()
print("Affectation des auditeurs de justice en stage juridictionnel")
time.sleep(.5)
print("(Paul Simon, AdJ. 2019 // paul.dc.simon@gmail.com)")
time.sleep(.5)
print()
print()
print()
print("Avez-vous bien lu le mode d'emploi ? (fichier 'README.pdf')")
time.sleep(2)
print()
print("Entrer le numéro du tour à simuler :")
n_rapport=input()
# TODO : à remettre à la fin
print("Ouverture du dossier \'tour_"+n_rapport+"\'")
time.sleep(.5)
print()
print("********************************************************************************")
print()
print("DÉBUT DU TRAITEMENT DES DONNEES")
print()
dossier="tour_"+n_rapport+"\\"   ### /!\ WINDOWS


# lecture des paramètres :
print("Lecture des paramètres :")
f = open("parametres.csv", newline='')
params_reader = csv.reader(f, delimiter=';', quotechar='|')
#print(params_reader[3])
#print(params_reader[12])
#print(params_reader[13])
#print(params_reader[14])
f.close()

# ouverture de la table des villes
print("Recensement des postes :")
nb_postes=0
nb_villes=0
f = open("postes.csv", newline='')
villes_reader = csv.reader(f, delimiter=';', quotechar='|')
villes=dict() # dictionnaire de Villes qui contient toutes les villes
for row in villes_reader:
	time.sleep(.1)
	if (int(row[1])>0):
		villes[row[0]]=Ville(nb_villes+1,row[0],int(row[1])) 
		nb_postes=nb_postes+int(row[1])
		nb_villes=nb_villes+1
		print(row[0]+" : "+row[1]+" poste(s)")
	else:
		print("Ville ignorée (aucun poste) : "+row[0])
		time.sleep(.5)
f.close()
print()
print("Il y a "+str(nb_postes)+" postes disponibles dans "+str(nb_villes)+" villes.")

next()

print()
print("Lecture de la liste des villes noires :")
villes_noires=list()
f = open("villes_noires.csv", newline='')
time.sleep(.5)
villes_reader = csv.reader(f, delimiter=';', quotechar='|')
for row in villes_reader:
	time.sleep(.1)
	villes_noires.append(row[0])
	print(row[0])
f.close()

print()
print("Lecture de la liste des villes rouges :")
time.sleep(.5)
villes_rouges=list()
f = open("villes_rouges.csv", newline='')
villes_reader = csv.reader(f, delimiter=';', quotechar='|')
for row in villes_reader:
	time.sleep(.1)
	villes_rouges.append(row[0])
	print(row[0])
f.close()
print()

print("Lecture de la liste des villes vertes :")
villes_vertes=list()
time.sleep(.5)
f = open("villes_vertes.csv", newline='')
villes_reader = csv.reader(f, delimiter=';', quotechar='|')
for row in villes_reader:
	time.sleep(.1)
	villes_vertes.append(row[0])
	print(row[0])
f.close()
print()

next()
f_err = open(dossier+"incidents_soumissions.txt","w")
# print("Nombre d'auditeurs : "+str(len(liste_logins)))
print("Ouverture du fichier \'"+dossier+"sondage.csv\'...")
time.sleep(.5)
csvfile=open(dossier+"sondage.csv", newline='')
reader = csv.reader(csvfile, delimiter=';', quotechar='|')

v=dict()
print("Lecture des voeux.")
time.sleep(.5)
for row in reader:
	aud=row[0].strip("\"\"")
	l=list()			
	for voeu in row[1:]:
		clean_voeu=nettoie(voeu)   
		if clean_voeu!='':
			l.append(clean_voeu)
	v[aud]=l

print()
print()

print("Validation des voeux  de chaque auditeur :")
print("(nombre de voeux suffisant, respect des règles de couleur,")
print("existence de chaque ville, absence de doublons)")
time.sleep(2)
nb_bons=0
nb_mauvais=0
n_voeux_et=0
for aud in v.keys():
	time.sleep(.05)
	n_rouge=compte_rouge(v[aud][:tot_voeux])
	n_noir=compte_noir(v[aud][:tot_voeux])
	n_vert=compte_vert(v[aud][:tot_voeux])
	# vérif taille
	if len(v[aud])<tot_voeux:
		print("Auditeur "+aud+"\t: ERREUR ! Pas assez de voeux")
		time.sleep(.5)
		v[aud] = []
		nb_mauvais=nb_mauvais+1
	# vérif existence
	elif not(villes_existantes(v[aud])):
		print("Auditeur "+aud+"\t: ERREUR ! Voeu inconnu :\t"+pb_villes_existantes(v[aud]))
		time.sleep(.5)
		v[aud] = []
		nb_mauvais=nb_mauvais+1
	# vérif unicité
	elif not(verifier_unicite_voeux(v[aud])):
		print("Auditeur "+aud+"\t: ERREUR ! Doublons :\t\t"+strfy(v[aud]))
		time.sleep(.5)
		v[aud] = []
		nb_mauvais=nb_mauvais+1
	# vérif couleurs
	elif (n_noir > noires_max) or (n_noir+n_rouge>rougesplusnoires_max) or (n_vert<vertes_min):
		print("Auditeur "+aud+"\t: ERREUR ! Couleurs ("+str(n_noir)+"N, "+str(n_rouge)+"R, "+str(n_vert)+"V) :\t"+strfy(v[aud]))
		time.sleep(.5)
		v[aud] = []
		nb_mauvais=nb_mauvais+1
	else :
		print("Auditeur "+aud+ " :\tvoeux validés")
		nb_bons=nb_bons+1
		if len(v[aud])>tot_voeux:
			n_voeux_et=n_voeux_et+1
print()
print("Voeux validés : "+str(nb_bons)+" auditeurs ; Voeux invalides : "+str(nb_mauvais)+" auditeurs.")
print(str(n_voeux_et)+" auditeurs sur "+str(nb_bons)+" ont formulé plus de "+str(tot_voeux)+" voeux")
f_err.close()
nb_aud=nb_bons+nb_mauvais
print()
print("Il y a "+str(nb_aud)+" auditeurs à répartir sur "+str(nb_postes)+" postes.")
volant=nb_postes-nb_aud

print()
next()
cas_part=list()

print("Lecture des cas particuliers :")
time.sleep(.5)
f = open(dossier+"/cas_part.csv", newline='')
cp_reader = csv.reader(f, delimiter=';', quotechar='|')
for row in cp_reader:
	time.sleep(.3)
	aud = row[0]
	n = int(row[1])
	print("L'auditeur "+aud+" doit être placé sur ses "+str(n)+" premiers voeux.")
	v[aud]=v[aud][:n]
	cas_part.append(aud)
f.close()
print()
time.sleep(1)
# Calcul du nb de villes n'ayant été demandées par personne :

demande_ville=dict()
demande_det=dict()

nb_postes_pourris = 0
for vil in villes.keys():
	demandee = False
	demande_ville[vil]=0
	demande_det[vil]=[0,0,0,0,0,0,0]
	for l in v.values():
		if vil in l:
			demandee = True
			demande_ville[vil]=demande_ville[vil]+1
			x=l.index(vil)
			if x < 6:
				demande_det[vil][x]=demande_det[vil][x]+1
			else:
				demande_det[vil][6]=demande_det[vil][6]+1
	if not(demandee):
		capa = villes[vil].capacite
		print("Aucun auditeur n'a placé "+vil+" dans ses voeux ("+str(capa)+" places)")
		time.sleep(.2)
		nb_postes_pourris=nb_postes_pourris+capa
print()
print("Il y a "+str(nb_postes_pourris)+" postes qui n'ont été demandés par personne.")
print("Taille du volant de postes : "+str(volant))
print()
if (nb_postes_pourris>volant) or (nb_mauvais>0):
	print("Il y aura forcément au moins "+str(max(nb_postes_pourris-volant,nb_mauvais))+" auditeurs placés hors de leurs voeux :(\n(dont "+str(nb_mauvais)+" pour cause de voeux invalides).")



print()
print("FIN DU TRAITEMENT DES DONNEES")
print()
next()
print("********************************************************************************")
print()
print("DÉBUT DE LA RÉPARTITION")



# on commence par démultiplier les colonnes de chaque ville, ie :
# on précise à quels indices correspond chaque ville
# et aussi à quelle ville correspond chaque indice du tableau

indice_vers_ville=list()
i=0
for vil in villes.values():
	for foo in range(vil.capacite):
		indice_vers_ville.append(vil.nom)
		vil.colonnes.append(i)
		i=i+1


# il faut aussi un matching a/r entre login de l'adj et indice dans la matrice

aud_vers_ind=dict()
ind_vers_aud=list()
i=0

auditeurs=list(v.keys())
random.seed(854769)
random.shuffle(auditeurs)
for aud in auditeurs:
	ind_vers_aud.append(aud)
	aud_vers_ind[aud]=i
	i=i+1

# Création de la grosse matrice
# lignes : nb_auditeurs ; colonnes : nb_postes
# On met une grosse valeur par défaut (mais pas trop grosse)

penalite = 10000000

nb_auditeurs=len(ind_vers_aud)
m=np.full((nb_auditeurs,nb_postes), penalite)

mbis=np.full((nb_auditeurs,nb_postes), 255)


# Remplissage de la matrice :
# pour chaque auditeur, on regarde les voeux dans l'ordre :
# pour chaque voeu, on met un nombre correspondant à l'ordre dans toutes les colonnes de la ville

for aud in v.keys():
	ligne = aud_vers_ind[aud]	
	for i in range(len(v[aud])):
		voeu_actuel = v[aud][i]		
		colonnes = villes[voeu_actuel].colonnes
		for col in colonnes:
			poids = i
			if i > (tot_voeux-1) :
				poids = (i-(tot_voeux-1))*penalite	
#			if (aud in cas_part):
#				poids=1
			m[ligne, col]=poids
			mbis[ligne, col]=((min(poids,tot_voeux))*255)/(tot_voeux+5)

V=v
# TODO : c'est ici qu'il faudrait rajouter les contraintes spécifiques aux auditeurs
image_2d = np.vstack(map(np.uint8, mbis.repeat(3,axis=0).repeat(3,axis=1)))
png.from_array(image_2d,mode="L").save(dossier+"voeux.png")
print()

# INVOCATION DE L'ALGO : 
print("Calcul de la répartition...")
time.sleep(3)
row_ind,col_ind=optimize.linear_sum_assignment(m)
print("Répartition terminée !")

time.sleep(1)
m_aff=np.full((nb_auditeurs,nb_postes), 0)
for i_aud in row_ind:
	m_aff[i_aud, col_ind[i_aud]]=1
print()

up=3
mter=np.full((nb_auditeurs,up*3*nb_postes), 255)
for aud in v.keys():
	ligne = aud_vers_ind[aud]	
	for i in range(len(v[aud])):
		voeu_actuel = v[aud][i]		
		colonnes = villes[voeu_actuel].colonnes
		for col in colonnes:
			poids = min(i,tot_voeux)
			x=((min(poids,tot_voeux))*255)/(tot_voeux+5)
			if (m_aff[ligne,col]==0):
				mter[ligne,up*3*col:up*3*col+up*3]=(x,x,x,x,x,x,x,x,x)
			else:
				z=(255,0,0,255,0,0,255,0,0)
				if poids==0:
					z=(0,255,0,0,255,0,0,255,0)
				if poids==1:
					z=(204,255,102,204,255,102,204,255,102)
				if poids==2:
					z=(255,102,0,255,102,0,255,102,0)	
				mter[ligne,up*3*col:up*3*col+up*3]=z

image_2d = np.vstack(map(np.uint8, mter.repeat(up,axis=0)))
png.from_array(image_2d,mode="RGB").save(dossier+"resultat.png")


print()

auditeurs=list(v.keys())
auditeurs.sort(key = int)
print()

print("Présentation des résultats (dans l'ordre des identifiants) :")
time.sleep(1)
aff_ville = dict()
rang_voeu_sat = dict()


for aud in auditeurs: 
	time.sleep(.06)
	i_aud=aud_vers_ind[aud]
	i_ville=col_ind[i_aud]
	n_ville=indice_vers_ville[i_ville]
	rang_voeu=1+m[i_aud,i_ville]
	n_complet_ville=n_ville
	if (rang_voeu>100):
		print("L'auditeur "+aud+" est affecté à "+n_complet_ville+" (hors voeux)")
		aff_ville[aud]=n_complet_ville
		rang_voeu_sat[aud]=-1
		time.sleep(.5)
	else:	
		print("L'auditeur "+aud+" est affecté à "+n_complet_ville+" (voeu numéro "+str(rang_voeu)+")")
		aff_ville[aud]=n_complet_ville
		rang_voeu_sat[aud]=rang_voeu
		
print()
print("FIN DE LA RÉPARTITION")
print()
next()
print("********************************************************************************")

print()
print("ANALYSE DES RÉSULTATS")
print()
time.sleep(.5)
poids = 0
xhv=0
for i in row_ind:
	x=m[i,col_ind[i]]
	if x < 100:
		poids = poids + 1+x
	else:
		xhv=xhv+1
print("Poids total : "+str(poids)+" + "+str(xhv)+" HV")
moy = round(float(poids) / float(nb_auditeurs),2)
print("(moyenne : "+str(moy)+" par auditeur)")

time.sleep(2)

print()
somme_voeux = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
hv = 0
for x in rang_voeu_sat.values():
	if x == -1:
		hv=hv+1	
	else:
		somme_voeux[x-1]=somme_voeux[x-1]+1

# Diagramme des satisfactions
labels=["Voeu 1","Voeu 2","Voeu 3","Voeu 4","Voeux 5 et plus"][:tot_voeux]
sizes = somme_voeux[:5]
for x in somme_voeux[5:]:
	sizes[4]=sizes[4]+x
sizes[4]=sizes[4]+hv
explode=(0.03,0.05,0.07,0.09,0.11,0.05,0.05,0,0,0,0,0,0,0,0,0,0,0,0,0,0)[:5]
#plt.bar(labels,sizes)
#plt.show()
fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=False, startangle=64)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

ax1.set_title('Degré de satisfaction')
fig1.tight_layout()
plt.savefig(dossier+"diagramme1.png")
plt.close()





for i in range(8):
	time.sleep(.5)
	x = somme_voeux[i]
	x_pc = round(x*100/nb_auditeurs,1)
	print("Il y a "+str(x)+" auditeurs affectés sur leur voeu n°"+str(i+1)+"\t\t("+str(x_pc)+"% des auditeurs)")
print()

hv_pc = round(hv*100/nb_auditeurs,1)
print("Il y a "+str(hv)+" auditeurs affectés hors de leurs voeux\t\t("+str(hv_pc)+"% des auditeurs)")
print()
time.sleep(.5)


L_dv=sorted(demande_ville.items(), key=lambda item: item[1])
# TODO : à produire en intégralité sur le fichier annexe
worst_10=L_dv[:10]
best_10=L_dv[-10:]

print("Les dix villes les plus demandées :")
for k,v in reversed(best_10):
	time.sleep(.2)
	print(k+" : "+str(v)+" auditeurs")
	
print()

print("Les dix villes les moins demandées :")
for k,v in worst_10:
	time.sleep(.2)
	print(k+" : "+str(v)+" auditeurs")
	


# diagramme demande des villes



labels = []
dem_val = []
place_val = []

for k,v in reversed(L_dv[-30:]):
	labels.append(k)
	dem_val.append(v)
	place_val.append(villes[k].capacite)


x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, dem_val, width, label='Demandes totales')
rects2 = ax.bar(x + width/2, place_val, width, label='Postes')

# Add some text for labels, title and custom x-axis tick labels, etc.
plt.xticks(rotation=90)
ax.set_title('Villes les plus demandées (total)')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()


def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom').set_fontsize(8)


autolabel(rects1)


fig.tight_layout()

plt.savefig(dossier+"diagramme2.png")
plt.close()


# Troisième diagramme
L_dv2=sorted(demande_det.items(), key=lambda item: item[1][0])

labels = []
dem_val = []
place_val = []

for k,v in reversed(L_dv2[-30:]):
	labels.append(k)
	dem_val.append(v[0])
	place_val.append(villes[k].capacite)


x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, dem_val, width, label='Demandes (en 1er voeu)')
rects2 = ax.bar(x + width/2, place_val, width, label='Postes')

# Add some text for labels, title and custom x-axis tick labels, etc.
plt.xticks(rotation=90)
ax.set_title('Villes les plus demandées (1er voeu)')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()


def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom').set_fontsize(8)


autolabel(rects1)


fig.tight_layout()

plt.savefig(dossier+"diagramme3.png")
plt.close()


time.sleep(.5)
print()
print("Postes encore libres à l'issue de la répartition :")
time.sleep(.5)
villes_encore_libres=dict(villes)
tot_libres=0
for v in aff_ville.values():
	villes_encore_libres[v].capacite=villes_encore_libres[v].capacite-1

for v in villes_encore_libres.values():
	if v.capacite!=0:
		tot_libres=tot_libres+v.capacite		
		print("Il reste "+str(v.capacite)+" place(s) libre(s) à "+v.nom)
		time.sleep(.2) 
print("Total : "+str(tot_libres)+" postes encore libres")

time.sleep(.5)

print()
print("Production des fichiers récapitulatifs")

time.sleep(1)

# Répartition par numéro
print("Création du fichier \'"+dossier+"repartition_par_id.csv (Répartition par identifiant)\'.")
csvfile=open(dossier+"repartition_par_id.csv", newline='', mode='w')
csvwriter=csv.writer(csvfile, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL)
csvwriter.writerow(["Identifiant","Ville obtenue","Rang du voeu satisfait","Voeu 1","Voeu 2","Voeu 3","Voeu 4","Voeu 5","Voeu 6"])
for aud in auditeurs:
	v_aff=aff_ville[aud]
	rg_v=str(rang_voeu_sat[aud])
	if rg_v=="-1":
		rg_v="HV"
	l=V[aud]
	csvwriter.writerow([aud,v_aff,rg_v]+l)
csvfile.close()

# Répartition par ville
print("Création du fichier \'"+dossier+"repartition_par_ville.csv (Répartition par ville)\'.")
time.sleep(1)
csvfile=open(dossier+"repartition_par_ville.csv", newline='', mode='w')
csvwriter=csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
csvwriter.writerow(["Identifiant","Ville obtenue","Rang du voeu satisfait","Voeu 1","Voeu 2","Voeu 3","Voeu 4","Voeu 5","Voeu 6"])
L_aff_villes=sorted(aff_ville.items(), key=lambda item: item[1])
for k,v in L_aff_villes:
	aud=k
	v_aff=v
	rg_v=str(rang_voeu_sat[aud])
	if rg_v=="-1":
		rg_v="HV"
	l=V[aud]
	csvwriter.writerow([aud,v_aff,rg_v]+l)
csvfile.close()

# Demandes par ville
print("Création du fichier \'"+dossier+"demande_par_ville.csv (Demande par ville)\'.")
time.sleep(.5)
csvfile=open(dossier+"demande_par_ville.csv", newline='', mode='w')
csvwriter=csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
csvwriter.writerow(["Ville","Demande totale","Voeu 1","Voeu 2","Voeu 3","Voeu 4","Voeu 5","Voeu 6","Autres"])
L_dem_villes=sorted(demande_det.items(), key=lambda item: item[1], reverse = True)
for k,v in L_dem_villes:
	dem_tot = sum(v)
	csvwriter.writerow([k,dem_tot]+v)
csvfile.close()
print()
print("Fin du programme ! Merci de l'avoir utilisé !")
time.sleep(5)














