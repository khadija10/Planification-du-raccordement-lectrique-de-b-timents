

############################ Importation des données et shapefiles ############################
# Import des bibliothèques nécessaires
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# Désactiver les avertissements inutiles
import warnings
warnings.filterwarnings("ignore")

# Définir le chemin du dossier de données
data_path = "../data/"  # adapte si besoin

# Charger les shapefiles des bâtiments et des infrastructures
batiments = gpd.read_file(data_path + "batiments.shp")
infrastructures = gpd.read_file(data_path + "infrastructures.shp")

# Charger les fichiers Excels du réseau
reseau = pd.read_excel(data_path + "reseau_en_arbre.xlsx")
batiments_aj = pd.read_excel(data_path + "batiments.xlsx")
infra_aj = pd.read_excel(data_path + "infra.xlsx")


# Vérification rapide
print("=== Aperçu des données ===")
print("Bâtiments :", len(batiments))
print("Infrastructures :", len(infrastructures))
print("Réseau :", len(reseau))
print("\nColonnes du réseau :", reseau.columns.tolist())

#  Afficher un aperçu
display(batiments.head())
display(infrastructures.head())
display(reseau.head())

##################################  Carto des shapefiles #################################

# Import
import matplotlib.pyplot as plt

# Créer 2 sous-graphes : 1 ligne, 2 colonnes
fig, axes = plt.subplots(1, 2, figsize=(16, 8))  # 1 ligne, 2 colonnes

# Carte 1 : Bâtiments
batiments.plot(ax=axes[0], color="brown", markersize=20)
axes[0].set_title("Bâtiments")
axes[0].axis('off')  # enlève les axes pour plus de clarté

# Carte 2 : Infrastructures
infrastructures.plot(ax=axes[1], color="black", linewidth=1)
axes[1].set_title("Infrastructures")
axes[1].axis('off')

# Affichage final
plt.suptitle("Cartes des bâtiments et infrastructures", fontsize=16)
plt.tight_layout()
plt.show()


##################### Statistiques sur les bâtiments & infrastructures ############################

# Statistiques sur les bâtiments

import sys as sns

print("===== Statistiques Bâtiments =====")
print("Nombre total de bâtiments :", len(batiments))
print("Nombre total de maisons :", batiments["nb_maisons"].sum())
print("\nStatistiques descriptives sur le nombre de maisons par bâtiment :")
display(batiments["nb_maisons"].describe())

#  Statistiques sur les infrastructures
print("\n===== Statistiques Infrastructures =====")
print("Nombre total de lignes :", len(infrastructures))
print("Longueur totale du réseau :", infrastructures["longueur"].sum())
print("\nStatistiques descriptives sur la longueur des lignes :")
display(infrastructures["longueur"].describe())

# Histogrammes côte à côte
fig, axes = plt.subplots(1, 2, figsize=(14,5))

# Histogramme nb_maisons
sys.histplot(batiments["nb_maisons"], bins=10, kde=True, color="orange", ax=axes[0])
axes[0].set_title("Distribution du nombre de maisons par bâtiment")
axes[0].set_xlabel("Nombre de maisons")
axes[0].set_ylabel("Nombre de bâtiments")

# Histogramme longueur
sns.histplot(infrastructures["longueur"], bins=10, kde=True, color="gray", ax=axes[1])
axes[1].set_title("Distribution des longueurs des lignes électriques")
axes[1].set_xlabel("Longueur")
axes[1].set_ylabel("Nombre de lignes")

plt.tight_layout()
plt.show()

##################### Fusion  ############################
# Charger la couche fusionnée
data_path = "../data/"
infra_merged = gpd.read_file(data_path + "infrastructures_fusionnee.shp")

# Vérifier les colonnes
print("Colonnes disponibles :", infra_merged.columns.tolist())
print("Types d'infrastructures :", infra_merged["infra_type"].unique())

# Carte des infrastructures selon leur type
fig, ax = plt.subplots(figsize=(10, 10))

# Palette de couleurs adaptée au nombre de types d'infra
unique_types = infra_merged["infra_type"].nunique()
palette = sns.color_palette("Set2", unique_types)

# Tracé coloré selon le type d’infrastructure
infra_merged.plot(
    ax=ax,
    column="infra_type",
    cmap="Set2",         # Palette de couleur
    legend=True,
    linewidth=2
)

ax.set_title("Carte des infrastructures par type", fontsize=14)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.axis('off')

plt.show()