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

def planifier_reparations(df_csv):
    """
    Planifie les réparations à partir du DataFrame des infrastructures et bâtiments.
    Le calcul se base sur la priorité (hôpital > école > habitation) et
    le ratio global (coût × durée / nb_maisons).
    """

    print("PLANIFICATION DES RÉPARATIONS (score global efficacité coût×durée/prises)")
    print("=" * 80)

    # --- Étape 1 : Création des objets Infra ---
    infra_dict = {}
    for _, row in df_csv.iterrows():
        infra_id = row['infra_id']
        if infra_id not in infra_dict:
            infra_dict[infra_id] = Infra(
                infra_id=infra_id,
                length=row.get('longueur', 0),
                infra_type=row.get('infra_type', ''),
                nb_houses=row.get('nb_maisons', 0),
                type_infra=row.get('type_infra', '')
            )

    # --- Étape 2 : Création des objets Batiment ---
    batiments_dict = {}
    for batiment_id, group in df_csv.groupby('id_batiment'):
        type_bat = str(group['type_batiment'].iloc[0]).strip().lower()
        infras = [infra_dict[i] for i in group['infra_id'].unique() if i in infra_dict]
        batiments_dict[batiment_id] = Batiment(batiment_id, type_bat, infras)

    # --- Étape 3 : Catégorisation des bâtiments ---
    batiments_intacts = [b for b in batiments_dict.values() if b.get_building_houses() == 0]
    batiments_a_reparer = [b for b in batiments_dict.values() if b.get_building_houses() > 0]

    print(f"{len(batiments_intacts)} bâtiments en phase 0 (aucune réparation nécessaire)")
    print(f"{len(batiments_a_reparer)} bâtiments nécessitent une intervention\n")

    # --- Étape 4 : Boucle de planification ---
    plan = []
    phase = 1

    while batiments_a_reparer:
        # Mise à jour des scores
        for b in batiments_a_reparer:
            b.get_priority_ratio()  # met à jour b.last_score

        # Tri combiné : priorité métier (via __lt__) + ratio
        batiments_a_reparer.sort()

        # Sélection du bâtiment le plus prioritaire
        best_b = batiments_a_reparer.pop(0)

        # Mise à jour du DataFrame d'origine
        infra_associees = [infra.infra_id for infra in best_b.list_infras]
        df_csv.loc[df_csv['infra_id'].isin(infra_associees), 'infra_type'] = 'infra_intacte'

        # Calcul des métriques
        cost = best_b.get_total_cost()
        duration = best_b.get_real_duration()
        houses = best_b.get_building_houses()
        ratio = best_b.last_score

        print(f"Phase {phase:02d} → Réparation de {best_b.id_building} "
              f"({best_b.type_batiment}) | coût={cost:,.0f}€, durée={duration:.1f}h, "
              f"prises={houses}, ratio={ratio:.3f}")

        plan.append({
            "phase": phase,
            "id_batiment": best_b.id_building,
            "type_batiment": best_b.type_batiment,
            "cout_total": cost,
            "duree_totale_h": duration,
            "nb_maisons": houses,
            "ratio": ratio,
            "score": best_b.last_score
        })

        
        # Réparation effective
        best_b.repair()

        # Mise à jour du DataFrame
        infra_associees = [infra.infra_id for infra in best_b.list_infras]
        df_csv.loc[df_csv['infra_id'].isin(infra_associees), 'infra_type'] = 'infra_intacte'

        # Recalcul du ratio des bâtiments restants (après réparation)
        for b in batiments_a_reparer:
            b.get_priority_ratio()
        
        # Mise à jour de la liste pour supprimer ceux déjà réparés
        batiments_a_reparer = [b for b in batiments_a_reparer if b.get_building_houses() > 0]

        phase += 1

    # --- Étape 5 : Résumé global ---
    total_cout = sum(p["cout_total"] for p in plan)
    total_duree = sum(p["duree_totale_h"] for p in plan)
    total_maisons = sum(p["nb_maisons"] for p in plan)

    print("\nPlanification terminée.")
    print(f"Coût total estimé : {total_cout:,.0f} €")
    print(f"Durée totale estimée : {total_duree:,.1f} h")
    print(f"Nombre total de prises raccordées : {total_maisons}\n")

    return pd.DataFrame(plan)

# ============================================================
# DÉCOUPAGE EN 4 PHASES (40 % / 20 % / 20 % / 20 %)
# ============================================================
def assigner_phases(plan_df):
    """
    Attribue automatiquement une phase de construction à chaque bâtiment,
    en priorisant les hôpitaux (phase 0) puis en répartissant les autres
    selon le coût cumulé du projet :
        - Phase 1 : 40 % du coût total
        - Phase 2 : 20 % suivants
        - Phase 3 : 20 % suivants
        - Phase 4 : 20 % restants
    """
    # Tri des bâtiments par score croissant (plus prioritaire = plus petit score)
    plan_df = plan_df.sort_values(by="score").reset_index(drop=True)

    # Coût total du projet
    total_cost = plan_df["cout_total"].sum()

    # Identification des hôpitaux
    hopital_index = plan_df.index[plan_df["type_batiment"].str.lower() == "hôpital"].tolist()

    # Seuils de répartition (cumul des coûts)
    seuils = {
        1: total_cost * 0.40,
        2: total_cost * 0.60,
        3: total_cost * 0.80,
        4: total_cost
    }

    plan_df["phase_construct"] = None
    cum_cost = 0

    for index, row in plan_df.iterrows():
        # Hôpitaux → phase 0 automatique
        if index in hopital_index:
            plan_df.at[index, "phase_construct"] = 0
            continue

        cum_cost += row["cout_total"]

        # Attribution selon le coût cumulé
        if cum_cost <= seuils[1]:
            plan_df.at[index, "phase_construct"] = 1
        elif cum_cost <= seuils[2]:
            plan_df.at[index, "phase_construct"] = 2
        elif cum_cost <= seuils[3]:
            plan_df.at[index, "phase_construct"] = 3
        else:
            plan_df.at[index, "phase_construct"] = 4

    # --- Résumé de la répartition ---
    print("\n=== RÉPARTITION AUTOMATIQUE EN 4 PHASES ===")
    couts_par_phase = plan_df.groupby("phase_construct")["cout_total"].sum()
    for phase, cout in couts_par_phase.items():
        print(f"Phase {int(phase)} → {cout:,.0f} €")

    print(f"\nCoût total réparti : {couts_par_phase.sum():,.0f} €\n")

    return plan_df

# ============================================================
# EXECUTION SIMULTANÉE PAR PHASE (4 ouvriers max/infra)
# ============================================================
def executer_phases(plan_df):
    print("=== DÉBUT DES PHASES DE TRAVAUX ===\n")

    projet_cout_total = 0
    projet_duree_total = 0
    projet_total_ouvriers = 0

    for phase_num in sorted(plan_df["phase_construct"].dropna().unique()):
        batiments_phase = plan_df[plan_df["phase_construct"] == phase_num]

        print(f"--- Phase {phase_num} ---")
        if phase_num == 0:
            print("→ Phase spéciale : HÔPITAL\n")

        phase_cout_total = 0
        phase_duree_max = 0
        total_ouvriers = 0

        # Tous les bâtiments de la phase sont réparés simultanément
        for _, row in batiments_phase.iterrows():
            nb_prises = row["nb_maisons"]
            cout_bat = row["cout_total"]
            duree_bat = row["duree_totale_h"]

            # 4 ouvriers par prise (selon ta logique précédente)
            nb_ouvriers = nb_prises * 4

            phase_cout_total += cout_bat
            phase_duree_max = max(phase_duree_max, duree_bat)
            total_ouvriers += nb_ouvriers

            print(f"  • {row['id_batiment']} ({row['type_batiment']}) → "
                  f"prises={nb_prises} × 4 ouvriers | coût={cout_bat:,.0f}€ | durée={duree_bat:.1f}h")

        projet_cout_total += phase_cout_total
        projet_duree_total += phase_duree_max  # durée du projet = somme des durées max des phases
        projet_total_ouvriers += total_ouvriers

        print("\nRésumé de la phase :")
        print(f"  → Coût total estimé : {phase_cout_total:,.0f} €")
        print(f"  → Durée totale estimée : {phase_duree_max:.1f} h (bâtiment le plus long)")
        print(f"  → Ouvriers mobilisés : {total_ouvriers} (4 par prise)\n")
        print(f"Fin de la phase {phase_num}. Tous les bâtiments de la phase sont réparés simultanément.\n")

    print("=== FIN DES PHASES DE TRAVAUX ===\n")

    # --- Résumé global du projet ---
    print("=== RÉSUMÉ DU PROJET ===")
    print(f"Coût total du projet : {projet_cout_total:,.0f} €")
    print(f"Durée totale du projet : {projet_duree_total:.1f} h")
    print(f"Total ouvriers mobilisés (toutes phases) : {projet_total_ouvriers}\n")

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
    
    
    plan_df = planifier_reparations(df)

    # --- Répartition en phases ---
    plan_df = assigner_phases(plan_df)

    # --- Exécution des phases ---
    executer_phases(plan_df)

    # --- Visualisation ---
    visualiser_phases(plan_df)

    print("\nPLANIFICATION TERMINÉE")
    print("=" * 60)



if __name__ == "__main__":
    main()
