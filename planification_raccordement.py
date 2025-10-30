# Planification du Raccordement Électrique de Bâtiments
# Implémentation complète avec visualisations et explications

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import networkx as nx
from pathlib import Path
from collections import defaultdict

from Infra import Infra
from Batiment import Batiment

# Configuration des graphiques
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)

def analyser_csv():
    print("ANALYSE DU FICHIER EXCEL MIS À JOUR")
    print("=" * 70)

    try:
        # --- Chargement du fichier Excel ---
        df = pd.read_excel('reseau_en_arbre_updated.xlsx')
        print("Fichier Excel chargé avec succès\n")

        # --- Vérification des colonnes ---
        colonnes_attendues = [
            'id_batiment', 'type_batiment', 'nb_maisons',
            'infra_id', 'infra_type', 'type_infra', 'longueur'
        ]
        if not all(col in df.columns for col in colonnes_attendues):
            raise ValueError("Colonnes manquantes dans le fichier Excel !")

        # --- Supprimer doublons éventuels ---
        df_clean = df.drop_duplicates().reset_index(drop=True)

        # --- Statistiques rapides ---
        print(f"Nombre total d’enregistrements : {len(df_clean)}")
        print(f"Nombre de bâtiments uniques : {df_clean['id_batiment'].nunique()}")
        print(f"Nombre d’infrastructures uniques : {df_clean['infra_id'].nunique()}")
        print(f"Longueur totale du réseau : {df_clean['longueur'].sum():.1f} m\n")

        return df_clean

    except Exception as e:
        print(f"Erreur lors de l’analyse du fichier : {e}")
        return None


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


def main():
    """
    Fonction principale
    """
    print("PLANIFICATION DU RACCORDEMENT ÉLECTRIQUE")
    print("=" * 60)


    # Étape : Analyse du CSV et Visualisation du réseau fusionné
    df = analyser_csv()

    if df is None:
        return

    # Étape 3 : Modélisation du réseau (orienté objects Infra et Batiment)
    # Étape 4 : Planification des réparations
    plan_df = planifier_reparations(df)
    
    print("PLANIFICATION TERMINÉE")
    print("=" * 60)

if __name__ == "__main__":
    main()