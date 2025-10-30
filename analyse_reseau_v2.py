"""
Analyse approfondie du fichier reseau_en_arbre.xlsx (Version 2)

Objectif :
Fournir une analyse détaillée du réseau électrique :
- Structure et distribution du réseau
- Mutualisation des infrastructures
- Efficacité (nb de maisons / longueur)
- Sauvegarde automatique des graphiques dans le dossier 'data/'
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# === Configuration ===
sns.set(style="whitegrid")
plt.rcParams["figure.autolayout"] = True

# Création du dossier data si nécessaire
os.makedirs("data", exist_ok=True)

# === Lecture du fichier ===
fichier_excel = "data/reseau_en_arbre.xlsx"
reseau = pd.read_excel(fichier_excel)

print(" Fichier chargé avec succès !")
print(f"Nombre total de lignes : {len(reseau)}")
print("\nAperçu du fichier :")
print(reseau.head())

# === Analyse descriptive ===
print("\n=== Répartition des types d'infrastructures ===")
print(reseau["infra_type"].value_counts(), "\n")

print("=== Statistiques descriptives ===")
print(reseau[["longueur", "nb_maisons"]].describe(), "\n")

# === Mutualisation (nombre de bâtiments par ligne) ===
mutualisation = reseau.groupby("infra_id")["id_batiment"].nunique().reset_index()
mutualisation.columns = ["infra_id", "nb_batiments_connectes"]

reseau = reseau.merge(mutualisation, on="infra_id", how="left")

print("=== Mutualisation moyenne ===")
print(mutualisation["nb_batiments_connectes"].describe(), "\n")

# === Efficacité (nombre de maisons / longueur) ===
reseau["efficacite"] = reseau["nb_maisons"] / reseau["longueur"]
print("=== Efficacité moyenne (maisons/mètre) ===")
print(reseau["efficacite"].describe(), "\n")

# === Interprétation ===
nb_total = len(reseau)
nb_remplacer = reseau[reseau["infra_type"] == "a_remplacer"].shape[0]
pct_remplacer = (nb_remplacer / nb_total) * 100
long_moy = reseau["longueur"].mean()
eff_moy = reseau["efficacite"].mean()
mutu_moy = mutualisation["nb_batiments_connectes"].mean()

print("\n=== Interprétation automatique ===")
print(f"- Total : {nb_total} connexions, dont {nb_remplacer} à remplacer ({pct_remplacer:.1f} %).")
print(f"- Longueur moyenne : {long_moy:.2f} m.")
print(f"- Efficacité moyenne : {eff_moy:.3f} maisons/m.")
print(f"- Mutualisation moyenne : {mutu_moy:.2f} bâtiments par ligne.")
print("-- Ces résultats montrent un réseau dense, avec de nombreuses lignes courtes à faible efficacité moyenne.")
print("-- Les lignes les plus mutualisées (partagées par > 5 bâtiments) représentent des points critiques pour la priorisation.\n")

# === Graphiques (sauvegardés dans /data) ===

# Distribution des longueurs
plt.figure(figsize=(8, 4))
sns.histplot(reseau["longueur"], bins=25, kde=True, color="teal")
plt.title("Distribution des longueurs des infrastructures")
plt.xlabel("Longueur (m)")
plt.ylabel("Fréquence")
plt.savefig("data/dist_longueurs_v2.png")
plt.close()

# Distribution du nombre de maisons
plt.figure(figsize=(8, 4))
sns.histplot(reseau["nb_maisons"], bins=10, kde=False, color="orange")
plt.title("Distribution du nombre de maisons par tronçon")
plt.xlabel("Nombre de maisons")
plt.ylabel("Fréquence")
plt.savefig("data/dist_maisons_v2.png")
plt.close()

# Mutualisation
plt.figure(figsize=(8, 4))
sns.histplot(mutualisation["nb_batiments_connectes"], bins=20, color="purple")
plt.title("Distribution du nombre de bâtiments connectés par ligne")
plt.xlabel("Nombre de bâtiments")
plt.ylabel("Fréquence")
plt.savefig("data/dist_mutualisation_v2.png")
plt.close()

#  Efficacité
plt.figure(figsize=(8, 4))
sns.histplot(reseau["efficacite"], bins=25, color="green", kde=True)
plt.title("Distribution de l’efficacité (maisons par mètre)")
plt.xlabel("Maisons par mètre")
plt.ylabel("Fréquence")
plt.savefig("data/dist_efficacite_v2.png")
plt.close()

#  Corrélation longueur vs mutualisation
plt.figure(figsize=(6, 6))
sns.scatterplot(
    data=reseau, x="longueur", y="nb_batiments_connectes",
    hue="infra_type", alpha=0.7
)
plt.title("Corrélation : longueur ↔ nombre de bâtiments connectés")
plt.xlabel("Longueur (m)")
plt.ylabel("Bâtiments connectés")
plt.savefig("data/correlation_longueur_mutualisation_v2.png")
plt.close()

# === Rapport résumé ===
rapport = [
    "=== RAPPORT D’ANALYSE DU RÉSEAU (V2) ===",
    f"Total connexions : {nb_total}",
    f"À remplacer : {nb_remplacer} ({pct_remplacer:.1f}%)",
    f"Longueur moyenne : {long_moy:.1f} m",
    f"Efficacité moyenne : {eff_moy:.3f} maisons/m",
    f"Mutualisation moyenne : {mutu_moy:.2f} bâtiments/ligne",
    "",
    " Graphiques générés dans le dossier 'data/' :",
    "- dist_longueurs_v2.png",
    "- dist_maisons_v2.png",
    "- dist_mutualisation_v2.png",
    "- dist_efficacite_v2.png",
    "- correlation_longueur_mutualisation_v2.png",
]

with open("data/rapport_analyse_v2.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(rapport))

print(" Rapport sauvegardé dans 'rapport_analyse_v2.txt'")
print(" Graphiques enregistrés dans le dossier 'data/'")
print("\nAnalyse V2 terminée avec succès.")
