"""
Analyse du fichier reseau_en_arbre.xlsx

Description :
Ce script effectue une analyse exploratoire complète du fichier 'reseau_en_arbre.xlsx'
afin de comprendre la structure du réseau électrique à reconstruire.
Il examine les types d’infrastructures, la distribution des longueurs,
le nombre de maisons connectées, et la mutualisation entre bâtiments.

Ce fichier est la base de la planification du raccordement électrique.
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# === Lecture du fichier Excel ===
fichier_excel = "data/reseau_en_arbre.xlsx"
reseau = pd.read_excel(fichier_excel)

print(" Fichier chargé avec succès !")
print(f"Nombre total de lignes : {len(reseau)}")
print("\nAperçu du fichier :")
print(reseau.head(), "\n")

# === Informations générales ===
print("=== Informations générales ===")
print(reseau.info(), "\n")

print("=== Noms de colonnes ===")
print(reseau.columns.tolist(), "\n")

# === Types d’infrastructures ===
print("=== Répartition des types d'infrastructures ===")
print(reseau["infra_type"].value_counts(), "\n")

# === Statistiques descriptives ===
print("=== Statistiques sur la longueur (m) ===")
print(reseau["longueur"].describe(), "\n")

print("=== Statistiques sur le nombre de maisons ===")
print(reseau["nb_maisons"].describe(), "\n")

# === Visualisations ===
plt.figure(figsize=(8, 4))
sns.histplot(reseau["longueur"], bins=20, kde=True, color="teal")
plt.title("Distribution des longueurs des infrastructures")
plt.xlabel("Longueur (m)")
plt.ylabel("Fréquence")
plt.show()

plt.figure(figsize=(8, 4))
sns.histplot(reseau["nb_maisons"], bins=10, color="orange")
plt.title("Distribution du nombre de maisons par tronçon")
plt.xlabel("Nombre de maisons")
plt.ylabel("Fréquence")
plt.show()

# === Mutualisation : nombre de bâtiments par ligne ===
mutualisation = reseau.groupby("infra_id")["id_batiment"].nunique().reset_index()
mutualisation.columns = ["infra_id", "nb_batiments_connectes"]

print("=== Mutualisation moyenne des lignes ===")
print(mutualisation.describe(), "\n")

plt.figure(figsize=(8, 4))
sns.histplot(mutualisation["nb_batiments_connectes"], bins=15, color="purple")
plt.title("Nombre de bâtiments connectés par infrastructure")
plt.xlabel("Nombre de bâtiments")
plt.ylabel("Fréquence")
plt.show()

# === Corrélation longueur -- mutualisation ===
merged = reseau.merge(mutualisation, on="infra_id")
plt.figure(figsize=(6, 6))
sns.scatterplot(data=merged, x="longueur", y="nb_batiments_connectes", hue="infra_type")
plt.title("Corrélation longueur ↔ nombre de bâtiments connectés")
plt.xlabel("Longueur (m)")
plt.ylabel("Nombre de bâtiments connectés")
plt.show()

print(" Analyse complète terminée !")
