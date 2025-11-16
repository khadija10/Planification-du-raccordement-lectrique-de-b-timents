# ============================================
# IMPORTS
# ============================================
import pandas as pd
import numpy as np
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
import warnings
warnings.filterwarnings("ignore")

# ============================================
# CHEMINS
# ============================================
base_path = r"C:\Users\AHassak\Desktop\HETIC\Refresher _ Optimisation Opérationnelle\Planification-du-raccordement-lectrique-de-b-timents\raccordement-electrique"
data_path = os.path.join(base_path, "outputs", "Donnees_Traiter", "Data_final.xlsx")
batiments_shp = os.path.join(base_path, "data", "batiments.shp")
infra_shp = os.path.join(base_path, "data", "infrastructures.shp")
output_path = os.path.join(base_path, "outputs")
os.makedirs(output_path, exist_ok=True)

# ============================================
# CHARGEMENT DES DONNÉES
# ============================================
Data_final = pd.read_excel(data_path)
print(f"✅ Données chargées : {Data_final.shape[0]} lignes, {Data_final.shape[1]} colonnes")

# Shapefiles
batiments_geo = gpd.read_file(batiments_shp)
infra_geo = gpd.read_file(infra_shp)

# ============================================
# NETTOYAGE
# ============================================
Data_final = Data_final.drop_duplicates(subset=["infra_id", "id_batiment"], keep="first")
num_cols = ["nb_maisons", "prix_metre", "duree_heure_metre", "prix_total (€)", "duree_totale (h)", "longueur"]
for col in num_cols:
    Data_final[col] = pd.to_numeric(Data_final[col], errors="coerce")

# ============================================
# CLASSES OBJETS
# ============================================
class Infra:
    def __init__(self, infra_id, longueur, nb_maisons, infra_type, type_infra, prix_total, duree_totale):
        self.infra_id = infra_id
        self.longueur = longueur
        self.nb_maisons = nb_maisons
        self.infra_type = infra_type
        self.type_infra = type_infra
        self.prix_total = prix_total
        self.duree_totale = duree_totale
        self.reparee = infra_type == "infra_intacte"

    def get_infra_difficulty(self):
        if self.nb_maisons == 0:
            return np.inf
        return self.longueur / self.nb_maisons

    def repair_infra(self):
        self.reparee = True

    def __repr__(self):
        return f"<Infra {self.infra_id} | {self.infra_type} | {self.longueur:.1f}m | rep={self.reparee}>"

class Batiment:
    def __init__(self, id_batiment, type_batiment, list_infras):
        self.id_batiment = id_batiment
        self.type_batiment = type_batiment
        self.list_infras = list_infras

    def get_building_difficulty(self):
        return sum([infra.get_infra_difficulty() for infra in self.list_infras if not infra.reparee])

    def __lt__(self, other):
        return self.get_building_difficulty() < other.get_building_difficulty()

    def __repr__(self):
        return f"<Bâtiment {self.id_batiment} ({self.type_batiment}) - diff={self.get_building_difficulty():.2f}>"

# ============================================
# CRÉATION DES OBJETS
# ============================================
infras_dict = {}
for _, row in Data_final.iterrows():
    infra = Infra(
        row["infra_id"],
        row["longueur"],
        row["nb_maisons"],
        row["infra_type"],
        row["type_infra"],
        row["prix_total (€)"],
        row["duree_totale (h)"]
    )
    infras_dict[row["infra_id"]] = infra

batiments_dict = {}
for id_bat, sub_df in Data_final.groupby("id_batiment"):
    infras = [infras_dict[iid] for iid in sub_df["infra_id"].unique() if iid in infras_dict]
    batiments_dict[id_bat] = Batiment(id_bat, sub_df["type_batiment"].iloc[0], infras)

print(f"🔧 {len(infras_dict)} infrastructures créées, {len(batiments_dict)} bâtiments modélisés")

# ============================================
# ALGO PLANIFICATION
# ============================================
COUT_HORAIRE = 300 / 8
NB_OUVRIERS_PAR_INFRA = 4
MARGE_HOPITAL = 0.2
AUTONOMIE_GENERATEUR_H = 20

phase_0 = [b for b in batiments_dict.values() if all(i.reparee for i in b.list_infras)]
to_repair = [b for b in batiments_dict.values() if any(not i.reparee for i in b.list_infras)]
planification = []

phase = 1
while to_repair:
    to_repair.sort()
    building = to_repair.pop(0)
    total_cost = 0
    total_time = 0
    ouvriers_utilises = 0
    infra_reparees = []

    for infra in building.list_infras:
        if not infra.reparee:
            infra.repair_infra()
            total_cost += infra.prix_total
            total_time += infra.duree_totale / NB_OUVRIERS_PAR_INFRA
            ouvriers_utilises += min(NB_OUVRIERS_PAR_INFRA, infra.nb_maisons)
            infra_reparees.append(infra.infra_id)

    if building.type_batiment.lower() == "hôpital":
        total_time *= 1 + MARGE_HOPITAL
        if total_time > AUTONOMIE_GENERATEUR_H:
            print(f"⚠️ L’hôpital {building.id_batiment} risque de dépasser le générateur ({total_time:.1f}h)")

    cout_ouvriers = total_time * COUT_HORAIRE
    planification.append({
        "Phase": phase,
        "Bâtiment": building.id_batiment,
        "Type": building.type_batiment,
        "Infra_reparees": ", ".join(infra_reparees),
        "Temps estimé (h)": round(total_time, 2),
        "Coût total (€)": round(total_cost + cout_ouvriers, 2),
        "Ouvriers utilisés": ouvriers_utilises
    })

    if len(planification) % 10 == 0:
        phase += 1

# ============================================
# EXPORT
# ============================================
planif_df = pd.DataFrame(planification)
export_path = os.path.join(output_path, "planification_raccordement_infra.xlsx")
planif_df.to_excel(export_path, index=False)
print(f"📊 Planification exportée : {export_path}")

# Totaux par phase
totaux_phase = planif_df.groupby("Phase").agg({
    "Temps estimé (h)": "sum",
    "Coût total (€)": "sum",
    "Ouvriers utilisés": "sum"
}).reset_index()
print("\n📌 Totaux par phase :")
print(totaux_phase)

####################################  Carte #####################

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import os

# ============================================
# CHEMINS
# ============================================
base_path = r"C:\Users\AHassak\Desktop\HETIC\Refresher _ Optimisation Opérationnelle\Planification-du-raccordement-lectrique-de-b-timents\raccordement-electrique"
planif_path = os.path.join(base_path, "outputs", "planification_raccordement_infra.xlsx")
batiments_shp = os.path.join(base_path, "data", "batiments.shp")
infra_shp = os.path.join(base_path, "data", "infrastructures.shp")
output_path = os.path.join(base_path, "outputs")
os.makedirs(output_path, exist_ok=True)

# ============================================
# CHARGEMENT
# ============================================
batiments = gpd.read_file(batiments_shp)
infrastructures = gpd.read_file(infra_shp)
planif_df = pd.read_excel(planif_path)

# ============================================
# EXPLOSION DE LA COLONNE Infra_reparees
# ============================================
# On sépare les infra_id et on crée une ligne par infra_id
planif_exploded = planif_df.assign(
    infra_id=planif_df["Infra_reparees"].str.split(", ")
).explode("infra_id")

# On ne garde que les colonnes nécessaires
planif_exploded = planif_exploded[["infra_id", "Phase"]]

# ============================================
# FUSION AVEC LE SHAPEFILE DES INFRASTRUCTURES
# ============================================
infra_merged = infrastructures.merge(planif_exploded, how="left", left_on="infra_id", right_on="infra_id")

# ============================================
# AJOUT DE LA PHASE AUX BATIMENTS
# ============================================
# On prend la phase la plus petite d’un bâtiment (ex: phase de la première infra réparée)
batiments_phase = planif_exploded.merge(
    planif_df[["Bâtiment", "Phase"]],
    left_on="infra_id", right_on="Infra_reparees",
    how="left"
).groupby("Bâtiment")["Phase"].min().reset_index()

batiments = batiments.merge(batiments_phase, how="left", left_on="id_batiment", right_on="Bâtiment")

# ============================================
# COULEURS
# ============================================
phase_colors = {1:"green", 2:"orange", 3:"purple", 4:"red", 0:"gray"}  # adapter selon nombre de phases
batiments["color"] = batiments["Phase"].map(phase_colors).fillna("gray")
infra_merged["color"] = infra_merged["Phase"].map(phase_colors).fillna("gray")

# ============================================
# PLOT
# ============================================
fig, ax = plt.subplots(figsize=(12,12))

# Infrastructures
for phase, color in phase_colors.items():
    infra_merged[infra_merged["Phase"]==phase].plot(ax=ax, color=color, linewidth=3, label=f"Infra phase {phase}")

# Bâtiments
for phase, color in phase_colors.items():
    batiments[batiments["Phase"]==phase].plot(ax=ax, marker='o', facecolor='none', edgecolor=color, markersize=50, linewidth=2, label=f"Bâtiment phase {phase}")

# Légende personnalisée
handles = []
for phase, color in phase_colors.items():
    handles.append(Line2D([0],[0], color=color, linewidth=3, label=f"Infra phase {phase}"))
    handles.append(Line2D([0],[0], marker='o', color=color, markerfacecolor='none', markersize=12, linewidth=2, label=f"Bâtiment phase {phase}"))
plt.legend(handles=handles, loc='best', fontsize=12)
plt.title("Carte des phases de raccordement", fontsize=16)
plt.axis("off")

# Sauvegarde
plt.tight_layout()
plt.savefig(os.path.join(output_path, "carte_phases_superposee.png"), dpi=300)
plt.show()

