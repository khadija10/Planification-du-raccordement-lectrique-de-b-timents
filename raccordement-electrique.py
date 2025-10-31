# ============================================
# IMPORTS
# ============================================
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# ============================================
# CHEMINS
# ============================================
base_path = r"C:\Users\AHassak\Desktop\HETIC\Refresher _ Optimisation Opérationnelle\Planification-du-raccordement-lectrique-de-b-timents\raccordement-electrique"
data_path = os.path.join(base_path, "outputs", "Donnees_Traiter", "Data_final.xlsx")
output_path = os.path.join(base_path, "outputs")
os.makedirs(output_path, exist_ok=True)

# ============================================
# CHARGEMENT DES DONNÉES
# ============================================
Data_final = pd.read_excel(data_path)
print(f"✅ Données chargées : {Data_final.shape[0]} lignes, {Data_final.shape[1]} colonnes")

# ============================================
# NETTOYAGE DE BASE
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

class Batiment:
    def __init__(self, id_batiment, type_batiment, list_infras):
        self.id_batiment = id_batiment
        self.type_batiment = type_batiment
        self.list_infras = list_infras

    def get_building_difficulty(self):
        return sum([infra.get_infra_difficulty() for infra in self.list_infras if not infra.reparee])

    def __lt__(self, other):
        return self.get_building_difficulty() < other.get_building_difficulty()

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
    for infra in building.list_infras:
        if not infra.reparee:
            infra.repair_infra()
            total_cost += infra.prix_total
            total_time += infra.duree_totale / NB_OUVRIERS_PAR_INFRA
            ouvriers_utilises += min(NB_OUVRIERS_PAR_INFRA, infra.nb_maisons)  # approximation

    if building.type_batiment.lower() == "hôpital":
        total_time *= 1 + MARGE_HOPITAL
        if total_time > AUTONOMIE_GENERATEUR_H:
            print(f"⚠️ Alerte : L’hôpital {building.id_batiment} risque de dépasser l’autonomie du générateur ({total_time:.1f}h)")

    cout_ouvriers = total_time * COUT_HORAIRE
    planification.append({
        "Phase": phase,
        "Bâtiment": building.id_batiment,
        "Type": building.type_batiment,
        "Temps estimé (h)": round(total_time, 2),
        "Coût total (€)": round(total_cost + cout_ouvriers, 2),
        "Nb ouvriers estimé": ouvriers_utilises
    })
    if len(planification) % 10 == 0:
        phase += 1

# ============================================
# EXPORT
# ============================================
planif_df = pd.DataFrame(planification)
export_path = os.path.join(output_path, "planification_raccordement-1.xlsx")
planif_df.to_excel(export_path, index=False)
print(f"📊 Planification exportée : {export_path}")

# ============================================
# SYNTHÈSE TOTALE
# ============================================
total_cout = planif_df["Coût total (€)"].sum()
total_duree = planif_df["Temps estimé (h)"].sum()
total_ouvriers = planif_df["Nb ouvriers estimé"].sum()
print(f"\n💰 Coût total : {total_cout:.2f} €")
print(f"⏱ Durée totale : {total_duree:.2f} h")
print(f"👷 Ouvriers totaux estimés : {total_ouvriers}")

# ============================================
# CARTE SIMPLIFIÉE DES PHASES
# ============================================
# Ici on peut juste représenter chaque bâtiment sur un scatter selon sa phase (exemple simple)
# On suppose qu'on a les coordonnées x et y pour chaque bâtiment dans Data_final
if "x_coord" in Data_final.columns and "y_coord" in Data_final.columns:
    merged = Data_final.merge(planif_df, left_on="id_batiment", right_on="Bâtiment", how="left")
    plt.figure(figsize=(10,8))
    scatter = plt.scatter(merged["x_coord"], merged["y_coord"], c=merged["Phase"], cmap="tab10", s=50)
    plt.colorbar(scatter, label="Phase")
    plt.title("Carte simplifiée des bâtiments par phase")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, "carte_phases.png"), dpi=300)
    plt.show()
else:
    print("ℹ️ Les coordonnées x_coord et y_coord n'existent pas, la carte ne sera pas tracée.")
