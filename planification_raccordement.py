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

def analyser_shapefiles():
    print("=" * 60)
    print("1. ANALYSE DES SHAPEFILES")
    print("=" * 60)

    try:
        # Chargement des shapefiles
        batiments_gdf = gpd.read_file('batiments.shp')
        infrastructures_gdf = gpd.read_file('infrastructures.shp')
        print()

        # Analyse des bâtiments
        print("ANALYSE DES BÂTIMENTS")
        print("-" * 30)
        print(f"Nombre total de bâtiments : {len(batiments_gdf)}")
        print(f"Système de coordonnées : {batiments_gdf.crs}")
        print(f"Colonnes disponibles : {list(batiments_gdf.columns)}")
        print(batiments_gdf.head())
        print()

        # Statistiques des bâtiments
        print("Statistiques des bâtiments :")
        batiments_stats = batiments_gdf.groupby('nb_maisons').size()
        for nb_maisons, count in batiments_stats.items():
            print(f"  - {count} bâtiments avec {nb_maisons} maison(s)")
        print()

        # Analyse des infrastructures
        print("ANALYSE DES INFRASTRUCTURES ÉLECTRIQUES")
        print("-" * 45)
        print(f"Nombre total d'infrastructures : {len(infrastructures_gdf)}")
        print(f"Système de coordonnées : {infrastructures_gdf.crs}")
        print(f"Colonnes disponibles : {list(infrastructures_gdf.columns)}")
        print(infrastructures_gdf.head())
        print()

        # Visualisation géographique
        print("VISUALISATION GÉOGRAPHIQUE")
        print("-" * 35)

        fig, axes = plt.subplots(1, 2, figsize=(20, 8))

        # Carte des bâtiments
        batiments_gdf.plot(ax=axes[0], color='lightblue', alpha=0.7, edgecolor='navy')
        axes[0].set_title('Disposition géographique des bâtiments')
        axes[0].set_xlabel('Longitude')
        axes[0].set_ylabel('Latitude')

        # Carte des infrastructures
        infrastructures_gdf.plot(ax=axes[1], color='orange', linewidth=2, alpha=0.8)
        axes[1].set_title('Réseau électrique existant')
        axes[1].set_xlabel('Longitude')
        axes[1].set_ylabel('Latitude')

        plt.tight_layout()
        plt.savefig('analyse_shapefiles.png', dpi=300, bbox_inches='tight')
        plt.show()

        print("Carte sauvegardée : 'analyse_shapefiles.png'")
        print()

        return batiments_gdf, infrastructures_gdf

    except Exception as e:
        print(f"Erreur lors du chargement des shapefiles : {e}")
        return None, None
    
def analyser_csv():
    print("2. ANALYSE DU FICHIER EXCEL MIS À JOUR")
    print("=" * 70)

    try:
        # --- Chargement du fichier Excel
        df = pd.read_excel('reseau_en_arbre_updated.xlsx')
        print("Fichier Excel chargé avec succès\n")

        # --- Vérification des colonnes
        colonnes_attendues = [
            'id_batiment', 'type_batiment', 'nb_maisons',
            'infra_id', 'infra_type', 'type_infra', 'longueur'
        ]
        if not all(col in df.columns for col in colonnes_attendues):
            raise ValueError("Colonnes manquantes dans le fichier Excel !")

        # --- Statistiques générales
        print("STATISTIQUES GÉNÉRALES")
        print("-" * 40)
        print(f"Nombre total d’enregistrements : {len(df)}")
        print(f"Nombre de bâtiments uniques : {df['id_batiment'].nunique()}")
        print(f"Nombre d’infrastructures uniques : {df['infra_id'].nunique()}")
        print(f"Longueur totale du réseau : {df['longueur'].sum():.1f} m")
        print()

        # --- Structure du fichier
        print("STRUCTURE DES DONNÉES")
        print("-" * 40)
        print("Colonnes disponibles :")
        for col in df.columns:
            print(f"  - {col}")
        print()

        # --- Analyse par type d'infrastructure
        print("ANALYSE PAR TYPE D'INFRASTRUCTURE")
        print("-" * 40)
        infra_stats = df.groupby('infra_type')['longueur'].agg(['count', 'sum', 'mean']).round(2)
        print(infra_stats)
        print()

        # --- Analyse par type de bâtiment
        print("ANALYSE PAR TYPE DE BÂTIMENT")
        print("-" * 40)
        batiment_stats = df.groupby('type_batiment').agg({
            'id_batiment': 'nunique',
            'longueur': 'sum',
            'nb_maisons': 'sum'
        }).round(2)
        print(batiment_stats)
        print()

        # --- Top 10 bâtiments les plus longs
        print("TOP 10 DES BÂTIMENTS PAR LONGUEUR TOTALE")
        print("-" * 40)
        batiment_detail = df.groupby('id_batiment').agg({
            'type_batiment': 'first',
            'longueur': 'sum',
            'nb_maisons': 'first'
        }).sort_values('longueur', ascending=False).head(10)
        for idx, row in batiment_detail.iterrows():
            print(f"  {idx} ({row['type_batiment']}): {row['longueur']:.1f}m, {row['nb_maisons']} maison(s)")
        print()

        # --- Visualisations clés
        print("VISUALISATIONS STATISTIQUES")
        print("-" * 40)

        sns.set_theme(style="whitegrid")
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle("Analyse du réseau électrique", fontsize=16)

        # Répartition des types d’infrastructure
        infra_counts = df['infra_type'].value_counts()
        axes[0,0].pie(infra_counts.values, labels=infra_counts.index, autopct='%1.1f%%',
                      colors=sns.color_palette("pastel"))
        axes[0,0].set_title("Répartition des types d’infrastructure")

        # Répartition des types de bâtiments
        bat_counts = df['type_batiment'].value_counts()
        axes[0,1].bar(bat_counts.index, bat_counts.values, color=sns.color_palette("Set2"))
        axes[0,1].set_title("Répartition des types de bâtiments")
        axes[0,1].set_ylabel("Nombre de bâtiments")

        # Longueur totale par type d’infrastructure
        infra_long = df.groupby('type_infra')['longueur'].sum().sort_values(ascending=False)
        axes[1,0].bar(infra_long.index, infra_long.values, color=sns.color_palette("crest"))
        axes[1,0].set_title("Longueur totale par type d’infrastructure")
        axes[1,0].set_ylabel("Longueur (m)")

        # Top 10 bâtiments par longueur
        axes[1,1].barh(batiment_detail.index.astype(str), batiment_detail['longueur'], color=sns.color_palette("flare"))
        axes[1,1].invert_yaxis()
        axes[1,1].set_title("Top 10 bâtiments par longueur totale")
        axes[1,1].set_xlabel("Longueur (m)")

        plt.tight_layout()
        plt.savefig('analyse_reseau.png', dpi=300, bbox_inches='tight')
        plt.show()

        print("Graphiques sauvegardés : 'analyse_reseau.png'\n")

        return df

    except Exception as e:
        print(f"Erreur lors de l’analyse du fichier : {e}")
        return None
    

def visualiser_reseau_fusionne(batiments_gdf, infrastructures_gdf, df_csv):
    print("=" * 60)
    print("3. VISUALISATION DU RÉSEAU FUSIONNÉ")
    print("=" * 60)

    try:
        # Vérifier les colonnes clés
        if 'infra_id' not in infrastructures_gdf.columns or 'infra_id' not in df_csv.columns:
            raise ValueError("Colonne 'infra_id' manquante dans les données !")

        # Fusionner les shapefiles d'infrastructures avec le CSV
        infra_merged = infrastructures_gdf.merge(
            df_csv[['infra_id', 'infra_type', 'id_batiment']],
            on='infra_id',
            how='left'
        )

        print(f"Fusion réussie : {len(infra_merged)} enregistrements après jointure")

        # Vérifier la présence des types d'infrastructure
        print(infra_merged['infra_type'].value_counts(dropna=False))
        print()

        # Création de la carte
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        ax.set_title("Réseau de raccordement : infrastructures et bâtiments")

        # Tracer les infrastructures intactes (vert)
        infra_intacte = infra_merged[infra_merged['infra_type'] == 'infra_intacte']
        if not infra_intacte.empty:
            infra_intacte.plot(ax=ax, color='green', linewidth=2, label='Infrastructures intactes')

        # Tracer les infrastructures à remplacer (rouge)
        infra_a_remplacer = infra_merged[infra_merged['infra_type'] == 'a_remplacer']
        if not infra_a_remplacer.empty:
            infra_a_remplacer.plot(ax=ax, color='red', linewidth=2, label='À remplacer')

        # Tracer les bâtiments
        batiments_gdf.plot(ax=ax, color='lightblue', alpha=0.6, edgecolor='navy', label='Bâtiments')

        # Mise en forme
        ax.legend()
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")

        plt.tight_layout()
        plt.savefig('reseau_fusionne.png', dpi=300, bbox_inches='tight')
        plt.show()

        print("Carte fusionnée sauvegardée : 'reseau_fusionne.png'")
        print()

        return infra_merged

    except Exception as e:
        print(f"Erreur lors de la fusion ou de la visualisation : {e}")
        return None


def modeliser_reseau(df_csv):
    print("3. MODÉLISATION DU RÉSEAU ÉLECTRIQUE")
    print("=" * 70)

    G = nx.Graph()

    # --- Étape 1 : création des nœuds (bâtiments)
    for _, row in df_csv.iterrows():
        bat_id = row['id_batiment']
        if bat_id not in G:
            G.add_node(
                bat_id,
                type=row['type_batiment'].lower().strip(),
                nb_maisons=int(row['nb_maisons']),
                batiment=None  # sera défini plus tard
            )

    # --- Étape 2 : création des arêtes (infrastructures)
    infra_grouped = df_csv.groupby('infra_id')['id_batiment'].unique()

    for infra_id, batiments in infra_grouped.items():
        batiments = list(batiments)
        if len(batiments) > 1:
            sub_df = df_csv[df_csv['infra_id'] == infra_id].iloc[0]

            # Création de l'objet Infra avec les colonnes correctes
            infra_obj = Infra(
                infra_id=infra_id,
                length=float(sub_df['longueur']),
                infra_type=sub_df['infra_type'].lower().strip(),  # 'a_remplacer' ou 'infra_intacte'
                nb_houses=int(sub_df['nb_maisons']),
                type_infra=sub_df['type_infra'].lower().strip()   # 'aerien', 'fourreau', etc.
            )

            # Connexion des bâtiments dans le graphe
            for i in range(len(batiments) - 1):
                b1, b2 = batiments[i], batiments[i + 1]
                G.add_edge(b1, b2, infra=infra_obj)

    print(f"Réseau modélisé : {len(G.nodes)} nœuds et {len(G.edges)} arêtes.\n")

    # --- Étape 3 : associer les objets Batiment à chaque nœud
    for node_id in G.nodes:
        connected_infras = [edata['infra'] for _, _, edata in G.edges(node_id, data=True)]
        bat_type = G.nodes[node_id]['type']
        G.nodes[node_id]['batiment'] = Batiment(node_id, bat_type, connected_infras)

    # --- Visualisation rapide
    pos = nx.spring_layout(G, seed=42)
    node_colors = [
        {'hôpital': 'red', 'école': 'blue', 'habitation': 'green'}.get(G.nodes[n]['type'], 'gray')
        for n in G.nodes
    ]

    plt.figure(figsize=(10, 7))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=800, font_size=8)
    plt.title("Modélisation du Réseau Électrique")
    plt.show()

    # --- Étape 4 : résumé synthétique
    cout_total = sum(
        edata['infra'].get_infra_cost()
        for _, _, edata in G.edges(data=True)
        if edata['infra'].infra_type == 'a_remplacer'
    )
    print(f"Coût total estimé des infrastructures à remplacer : {cout_total:,.0f} €")

    return G


def planifier_reparations(df_csv, G):
    print("5. PLANIFICATION DES RÉPARATIONS")
    print("=" * 70)

    # --- Étape 1 : Reconstituer les objets Infra
    infra_dict = {}
    for _, row in df_csv.iterrows():
        infra_id = row['infra_id']
        if infra_id not in infra_dict:
            infra_dict[infra_id] = Infra(
                infra_id=infra_id,
                length=float(row['longueur']),
                infra_type=row['infra_type'],   
                nb_houses=int(row['nb_maisons']),
                type_infra=row['type_infra']
            )

    # --- Étape 2 : Reconstituer les objets Bâtiment
    batiments_dict = {}
    for batiment_id, group in df_csv.groupby('id_batiment'):
        type_batiment = group['type_batiment'].iloc[0]
        infras = [infra_dict[i] for i in group['infra_id'].unique()]
        batiments_dict[batiment_id] = Batiment(
            id_building=batiment_id,
            type_batiment=type_batiment,
            list_infras=infras
        )

    # --- Étape 3 : Identifier les bâtiments à réparer
    batiments_a_reparer = [
        b for b in batiments_dict.values()
        if any(infra.infra_type == "a_remplacer" for infra in b.list_infras)
    ]
    batiments_intacts = [
        b for b in batiments_dict.values()
        if all(infra.infra_type != "a_remplacer" for infra in b.list_infras)
    ]

    print(f"{len(batiments_intacts)} bâtiments intacts (aucune réparation nécessaire)")
    print(f"{len(batiments_a_reparer)} bâtiments nécessitent des réparations\n")

    # --- Étape 4 : Planification dynamique
    plan = []
    phase = 1

    while batiments_a_reparer:
        # Sélection via le score basé sur le graphe
        batiment_cible = max(
            batiments_a_reparer,
            key=lambda b: b.get_priority_score_graph(G)
        )

        difficulte = batiment_cible.get_building_difficulty()
        cout = batiment_cible.get_building_cost()
        duree = batiment_cible.get_building_duration()
        score_graph = batiment_cible.get_priority_score_graph(G)

        print(
            f"Phase {phase}: Réparation de {batiment_cible.id_building} "
            f"({batiment_cible.type_batiment}) | "
            f"difficulté={difficulte:.2f}, coût={cout:,.0f}€, "
            f"durée={duree:.1f}h, score_graph={score_graph:.2f}"
        )

        # Étape de réparation
        batiment_cible.repair()

        # Enregistrement dans le plan
        plan.append({
            "phase": phase,
            "id_batiment": batiment_cible.id_building,
            "type_batiment": batiment_cible.type_batiment,
            "difficulte_batiment": difficulte,
            "cout_total": cout,
            "duree_totale_h": duree,
            "score_priorite_graph": score_graph
        })

        # Mise à jour de la liste
        batiments_a_reparer.remove(batiment_cible)
        batiments_a_reparer = [
            b for b in batiments_a_reparer
            if any(infra.infra_type == "a_remplacer" for infra in b.list_infras)
        ]

        phase += 1

    # --- Étape 5 : Résumé global
    print("\nPlanification terminée : tous les bâtiments ont été réparés.")
    total_cout = sum(p["cout_total"] for p in plan)
    total_duree = sum(p["duree_totale_h"] for p in plan)
    print(f"Coût total estimé du plan : {total_cout:,.0f} €")
    print(f"Durée totale estimée : {total_duree:,.1f} h\n")

    # --- Étape 6 : Retour du plan sous forme de DataFrame
    df_plan = pd.DataFrame(plan)
    return df_plan


def main():
    """
    Fonction principale
    """
    print("PLANIFICATION DU RACCORDEMENT ÉLECTRIQUE")
    print("=" * 60)

    # Étape 1 : Analyse des shapefiles
    # batiments_gdf, infrastructures_gdf = analyser_shapefiles()

    # Étape 2 : Analyse du CSV et Visualisation du réseau fusionné
    df = analyser_csv()
    # infra_merged = visualiser_reseau_fusionne(batiments_gdf, infrastructures_gdf, df)  
    # 
    # print(df.head()) 

    if df is None:
        return

    # Étape 3 : Modélisation du réseau
    G = modeliser_reseau(df)
    # Étape 4 : Planification des réparations
    plan_df = planifier_reparations(df, G)
    
    print("PLANIFICATION TERMINÉE")
    print("=" * 60)

if __name__ == "__main__":
    main()