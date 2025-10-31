import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from Infra import Infra
from Batiment import Batiment

# --- Configuration graphique ---
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)


# ============================================================
#  ANALYSE DU FICHIER EXCEL
# ============================================================

def analyser_csv():
    print("ANALYSE DU FICHIER EXCEL MIS À JOUR")
    print("=" * 70)

    try:
        df = pd.read_excel('reseau_en_arbre_updated.xlsx')
        print("Fichier Excel chargé avec succès\n")

        colonnes_attendues = [
            'id_batiment', 'type_batiment', 'nb_maisons',
            'infra_id', 'infra_type', 'type_infra', 'longueur'
        ]
        if not all(col in df.columns for col in colonnes_attendues):
            raise ValueError("Colonnes manquantes dans le fichier Excel !")

        df_clean = df.drop_duplicates().reset_index(drop=True)

        print(f"Nombre total d’enregistrements : {len(df_clean)}")
        print(f"Nombre de bâtiments uniques : {df_clean['id_batiment'].nunique()}")
        print(f"Nombre d’infrastructures uniques : {df_clean['infra_id'].nunique()}")
        print(f"Longueur totale du réseau : {df_clean['longueur'].sum():.1f} m\n")

        return df_clean

    except Exception as e:
        print(f"Erreur lors de l’analyse du fichier : {e}")
        return None


# ============================================================
#  PLANIFICATION DES RÉPARATIONS
# ============================================================

# ============================================================
# DÉCOUPAGE EN 4 PHASES (40 % / 20 % / 20 % / 20 %)
# ============================================================

def assigner_phases(plan_df):
    plan_df = plan_df.sort_values(by="score").reset_index(drop=True)
    total_cost = plan_df["cout_total"].sum()

    hopital_index = plan_df.index[plan_df["type_batiment"] == "hôpital"].tolist()

    seuils = {
        "phase_1": total_cost * 0.40,
        "phase_2": total_cost * 0.60,
        "phase_3": total_cost * 0.80,
        "phase_4": total_cost
    }

    plan_df["phase_construct"] = None
    cum_cost = 0

    for index, row in plan_df.iterrows():
        if index in hopital_index:
            plan_df.at[index, "phase_construct"] = 0
            continue

        cum_cost += row["cout_total"]
        if cum_cost <= seuils["phase_1"]:
            plan_df.at[index, "phase_construct"] = 1
        elif cum_cost <= seuils["phase_2"]:
            plan_df.at[index, "phase_construct"] = 2
        elif cum_cost <= seuils["phase_3"]:
            plan_df.at[index, "phase_construct"] = 3
        else:
            plan_df.at[index, "phase_construct"] = 4

    print("\nRépartition automatique en 4 phases terminée")
    print(plan_df.groupby("phase_construct")["cout_total"].sum(), "\n")

    return plan_df


# ============================================================
# EXECUTION SIMULTANÉE PAR PHASE (4 ouvriers max/infra)
# ============================================================
def executer_phases(plan_df, batiments_dict, infra_dict):
    print("=== DÉBUT DES PHASES DE TRAVAUX ===\n")

    for phase_num in sorted(plan_df["phase_construct"].unique()):
        batiments_phase = plan_df[plan_df["phase_construct"] == phase_num]

        print(f"--- Phase {phase_num} ---")
        if phase_num == 0:
            print("→ Phase spéciale : HÔPITAL\n")

        phase_cout_total = 0
        phase_duree_max = 0
        total_ouvriers = 0

        # Tous les bâtiments sont réparés simultanément
        for _, row in batiments_phase.iterrows():
            bat = batiments_dict[row["id_batiment"]]
            nb_prises = bat.get_building_houses()
            nb_ouvriers = nb_prises * 4  # 4 ouvriers par prise

            cout_bat = bat.get_total_cost()
            duree_bat = bat.get_real_duration()

            phase_cout_total += cout_bat
            phase_duree_max = max(phase_duree_max, duree_bat)
            total_ouvriers += nb_ouvriers

            print(f"  • {bat.id_building} ({bat.type_batiment}) → "
                  f"prises={nb_prises} × 4 ouvriers | coût={cout_bat:,.0f}€ | durée={duree_bat:.1f}h")

        print("\nRésumé de la phase :")
        print(f"  → Coût total estimé : {phase_cout_total:,.0f} €")
        print(f"  → Durée totale estimée : {phase_duree_max:.1f} h (la plus longue des réparations)")
        print(f"  → Ouvriers mobilisés : {total_ouvriers} (4 par prise)\n")

        print(f"Fin de la phase {phase_num}. Tous les bâtiments de la phase sont réparés simultanément.\n")

    print("=== FIN DES PHASES DE TRAVAUX ===\n")


# ============================================================
# VISUALISATION
# ============================================================

def visualiser_phases(plan_df):
    plt.figure(figsize=(10, 6))
    sns.barplot(x="phase_construct", y="cout_total", data=plan_df, estimator=sum, ci=None)
    plt.title("Répartition des coûts par phase de construction")
    plt.xlabel("Phase de construction")
    plt.ylabel("Coût total (€)")
    plt.grid(True, alpha=0.3)
    plt.show()


# ============================================================
# MAIN
# ============================================================
def main():
    print("PLANIFICATION DU RACCORDEMENT ÉLECTRIQUE")
    print("=" * 60)

    df = analyser_csv()
    if df is None:
        return

    # --- Création des objets Infra et Bâtiments ---
    infra_dict = {}
    for _, row in df.iterrows():
        infra_id = row['infra_id']
        if infra_id not in infra_dict:
            infra_dict[infra_id] = Infra(
                infra_id=infra_id,
                length=row.get('longueur', 0),
                infra_type=row.get('infra_type', ''),
                nb_houses=row.get('nb_maisons', 0),
                type_infra=row.get('type_infra', '')
            )

    batiments_dict = {}
    for batiment_id, group in df.groupby('id_batiment'):
        type_bat = str(group['type_batiment'].iloc[0]).strip().lower()
        infras = [infra_dict[infra] for infra in group['infra_id'].unique() if infra in infra_dict]
        batiments_dict[batiment_id] = Batiment(batiment_id, type_bat, infras)

    # --- Construction de plan_df directement ---
    plan = []
    for bat in batiments_dict.values():
        houses = bat.get_building_houses()
        if houses > 0:
            bat.get_priority_ratio()
            plan.append({
                "id_batiment": bat.id_building,
                "type_batiment": bat.type_batiment,
                "cout_total": bat.get_total_cost(),
                "duree_totale_h": bat.get_real_duration(),
                "nb_maisons": houses,
                "score": bat.last_score
            })

    plan_df = pd.DataFrame(plan)
    plan_df = assigner_phases(plan_df)

    # --- Exécution des phases directement ---
    executer_phases(plan_df, batiments_dict, infra_dict)

    # --- Visualisation ---
    visualiser_phases(plan_df)

    print("\nPLANIFICATION TERMINÉE")
    print("=" * 60)



if __name__ == "__main__":
    main()
