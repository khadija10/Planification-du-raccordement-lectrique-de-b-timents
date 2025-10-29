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
   
    print("2. ANALYSE DU FICHIER CSV")
    print("=" * 60)

    try:
        # Chargement du fichier Excel
        df = pd.read_excel('reseau_en_arbre.xlsx')

        print("Fichier Excel chargé avec succès")
        print()

        # Statistiques générales
        print("STATISTIQUES GÉNÉRALES")
        print("-" * 25)
        print(f"Nombre total d'enregistrements : {len(df)}")
        print(f"Nombre de bâtiments uniques : {df['id_batiment'].nunique()}")
        print(f"Nombre d'infrastructures uniques : {df['infra_id'].nunique()}")
        print()

        # Structure des données
        print("STRUCTURE DES DONNÉES")
        print("-" * 25)
        print("Colonnes disponibles :")
        for col in df.columns:
            print(f"  - {col}")
        print()

        # Analyse par type d'infrastructure
        print("ANALYSE PAR TYPE D'INFRASTRUCTURE")
        print("-" * 40)

        infra_stats = df.groupby('infra_type').agg({
            'longueur': ['count', 'sum', 'mean', 'min', 'max'],
            'id_batiment': 'nunique'
        }).round(2)

        print("Statistiques par type d'infrastructure :")
        print(infra_stats)
        print()

        # Analyse par bâtiment
        print("ANALYSE PAR BÂTIMENT")
        print("-" * 25)

        batiment_stats = df.groupby('id_batiment').agg({
            'nb_maisons': 'first',
            'longueur': ['count', 'sum'],
            'infra_type': lambda x: (x == 'a_remplacer').sum()
        }).round(2)

        batiment_stats.columns = ['nb_maisons', 'nb_segments', 'longueur_totale', 'nb_a_remplacer']

        print("Top 10 bâtiments par longueur totale :")
        top_10 = batiment_stats.nlargest(10, 'longueur_totale')
        for idx, row in top_10.iterrows():
            print(f"  {idx}: {row['longueur_totale']:.2f}m total, {int(row['nb_maisons'])} maison(s), {int(row['nb_segments'])} segments")
        print()

        # Analyse des coûts totaux
        print("ANALYSE DES COÛTS")
        print("-" * 20)

        total_longueur_intacte = df[df['infra_type'] == 'infra_intacte']['longueur'].sum()
        total_longueur_remplacer = df[df['infra_type'] == 'a_remplacer']['longueur'].sum()
        total_maisons = df.groupby('id_batiment')['nb_maisons'].first().sum()

        print(f"Longueur totale infrastructures intactes : {total_longueur_intacte:.2f} m")
        print(f"Longueur totale à remplacer : {total_longueur_remplacer:.2f} m")
        print(f"Total maisons à raccorder : {total_maisons}")
        print(f"Coût estimé total (longueur à remplacer) : {total_longueur_remplacer:.2f} m")
        print()

        # Analyse de la mutualisation
        print("ANALYSE DE LA MUTUALISATION")
        print("-" * 30)

        infra_connexions = df.groupby('infra_id').agg({
            'id_batiment': list,
            'longueur': 'first',
            'infra_type': 'first'
        }).reset_index()

        # Infrastructures mutualisées (partagées par plusieurs bâtiments)
        infra_mutualisees = infra_connexions[infra_connexions['id_batiment'].apply(len) > 1]

        print(f"Infrastructures mutualisées : {len(infra_mutualisees)}/{len(infra_connexions)} ({len(infra_mutualisees)/len(infra_connexions)*100:.1f}%)")
        print(f"Longueur mutualisée : {infra_mutualisees['longueur'].sum():.2f} m")

        # Distribution du nombre de bâtiments par infrastructure
        mutualisation_dist = infra_mutualisees['id_batiment'].apply(len).value_counts().sort_index()
        print("Distribution de la mutualisation :")
        for nb_batiments, count in mutualisation_dist.items():
            print(f"  - {count} infrastructures partagées par {nb_batiments} bâtiments")
        print()

        # Graphiques d'analyse
        print("VISUALISATIONS STATISTIQUES")
        print("-" * 35)

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Analyse du réseau électrique - Statistiques générales', fontsize=16)

        # 1. Distribution des types d'infrastructure
        infra_counts = df['infra_type'].value_counts()
        axes[0,0].pie(infra_counts.values, labels=infra_counts.index, autopct='%1.1f%%')
        axes[0,0].set_title('Répartition des types d\'infrastructure')

        # 2. Distribution des longueurs par type
        sns.boxplot(data=df, x='infra_type', y='longueur', ax=axes[0,1])
        axes[0,1].set_title('Distribution des longueurs par type d\'infrastructure')
        axes[0,1].set_ylabel('Longueur (m)')

        # 3. Nombre de maisons par bâtiment
        maisons_dist = df.groupby('id_batiment')['nb_maisons'].first().value_counts().sort_index()
        axes[1,0].bar(maisons_dist.index, maisons_dist.values)
        axes[1,0].set_title('Distribution du nombre de maisons par bâtiment')
        axes[1,0].set_xlabel('Nombre de maisons')
        axes[1,0].set_ylabel('Nombre de bâtiments')

        # 4. Top 10 bâtiments par longueur
        top_10_plot = batiment_stats.nlargest(10, 'longueur_totale')
        axes[1,1].bar(range(len(top_10_plot)), top_10_plot['longueur_totale'])
        axes[1,1].set_title('Top 10 bâtiments par longueur totale de réseau')
        axes[1,1].set_xlabel('Bâtiment (index)')
        axes[1,1].set_ylabel('Longueur totale (m)')
        axes[1,1].set_xticks(range(len(top_10_plot)))
        axes[1,1].set_xticklabels([f'E{i+1}' for i in range(len(top_10_plot))], rotation=45)

        plt.tight_layout()
        plt.savefig('analyse_csv.png', dpi=300, bbox_inches='tight')
        plt.show()

        print("Graphiques sauvegardés : 'analyse_csv.png'")
        print()

        return df

    except Exception as e:
        print(f"Erreur lors du chargement du fichier CSV : {e}")
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
    print("=" * 60)
    print("4. MODÉLISATION DU RÉSEAU ÉLECTRIQUE (GRAPHE)")
    print("=" * 60)

    try:
        # Création du graphe non orienté
        G = nx.Graph()

        # --- Étape 1 : Ajouter les nœuds (bâtiments)
        batiments = df_csv['id_batiment'].unique()
        for bat in batiments:
            nb_maisons = df_csv.loc[df_csv['id_batiment'] == bat, 'nb_maisons'].iloc[0]
            G.add_node(bat, nb_maisons=nb_maisons)
        print(f"Nœuds ajoutés : {len(G.nodes)} bâtiments")

        # --- Étape 2 : Ajouter les arêtes (infrastructures)
        for _, row in df_csv.iterrows():
            infra_id = row['infra_id']
            infra_type = row['infra_type']
            longueur = row['longueur']
            id_batiment = row['id_batiment']

            # Définition d’un coût (pondération)
            if infra_type == 'a_remplacer':
                cout = longueur * 1.0  # tu peux définir un vrai barème ici
            elif infra_type == 'infra_intacte':
                cout = longueur * 0.2
            else:
                cout = longueur * 0.5  # par défaut

            # Ajouter une arête entre le bâtiment et l’infrastructure virtuelle
            G.add_edge(f"infra_{infra_id}", f"bat_{id_batiment}",
                       infra_id=infra_id,
                       infra_type=infra_type,
                       longueur=longueur,
                       cout=cout)

        print(f"Arêtes ajoutées : {len(G.edges)} connexions")

        # --- Étape 3 : Statistiques de connectivité
        print("\nSTATISTIQUES DU GRAPHE")
        print("-" * 30)
        print(f"Composantes connexes : {nx.number_connected_components(G)}")
        print(f"Degré moyen : {sum(dict(G.degree()).values()) / len(G.nodes):.2f}")

        # --- Étape 4 : Visualisation rapide du graphe
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G, seed=42, k=0.3)

        # Couleur selon type d’infra
        edge_colors = [
            'red' if G[u][v]['infra_type'] == 'a_remplacer' else 'green'
            for u, v in G.edges
        ]

        nx.draw(
            G,
            pos,
            node_size=80,
            node_color='skyblue',
            edge_color=edge_colors,
            with_labels=False,
            alpha=0.7
        )
        plt.title("Modélisation du réseau électrique (graphe)")
        plt.tight_layout()
        plt.savefig("graphe_reseau.png", dpi=300, bbox_inches='tight')
        plt.show()

        print("Graphe sauvegardé : 'graphe_reseau.png'")
        print()

        return G

    except Exception as e:
        print(f"Erreur lors de la modélisation du réseau : {e}")
        return None

def planifier_reparations(df_csv):
    print("5. PLANIFICATION DES RÉPARATIONS")
    print("=" * 60)

    # Créer les objets Infra
    infra_dict = {}
    for _, row in df_csv.iterrows():
        infra_id = row['infra_id']
        if infra_id not in infra_dict:
            infra_dict[infra_id] = Infra(
                infra_id=infra_id,
                length=row['longueur'],
                infra_type=row['infra_type'],
                nb_houses=row['nb_maisons']
            )

    # Créer les objets Batiment
    batiments_dict = {}
    for batiment_id, group in df_csv.groupby('id_batiment'):
        infras = [infra_dict[i] for i in group['infra_id'].unique()]
        batiments_dict[batiment_id] = Batiment(batiment_id, infras)

    # Identifier les bâtiments impactés
    batiments_a_reparer = [
        b for b in batiments_dict.values() if b.get_building_difficulty() > 0
    ]
    batiments_intacts = [
        b for b in batiments_dict.values() if b.get_building_difficulty() == 0
    ]

    print(f"{len(batiments_intacts)} bâtiments en phase 0 (aucune réparation nécessaire)")
    print(f"{len(batiments_a_reparer)} bâtiments nécessitent des réparations\n")

    # Boucle principale
    plan = []
    phase = 1

    while batiments_a_reparer:
        # Sélectionner le bâtiment le moins difficile à ce stade
        batiment_min = min(batiments_a_reparer, key=lambda b: b.get_building_difficulty())
        difficulte = batiment_min.get_building_difficulty()

        print(f"Phase {phase}: Réparation du bâtiment {batiment_min.id_building} (difficulté = {difficulte:.2f})")

        # Réparer ses infras
        batiment_min.repair()

        # Ajouter au plan
        plan.append({
            "phase": phase,
            "id_batiment": batiment_min.id_building,
            "difficulte_batiment": difficulte
        })

        # Retirer le bâtiment réparé
        batiments_a_reparer.remove(batiment_min)

        # Recalculer les difficultés restantes
        batiments_a_reparer = [
            b for b in batiments_a_reparer if b.get_building_difficulty() > 0
        ]

        phase += 1

    print("\nPlanification terminée : tous les bâtiments ont été réparés.")
    return pd.DataFrame(plan)



def main():
    """
    Fonction principale
    """
    print("PLANIFICATION DU RACCORDEMENT ÉLECTRIQUE")
    print("=" * 60)

    # Étape 1 : Analyse des shapefiles
    batiments_gdf, infrastructures_gdf = analyser_shapefiles()

    # Étape 2 : Analyse du CSV et Visualisation du réseau fusionné
    df = analyser_csv()
    infra_merged = visualiser_reseau_fusionne(batiments_gdf, infrastructures_gdf, df)   

    if df is None:
        return

    # Étape 3 : Modélisation du réseau
    G = modeliser_reseau(df)

    df_reparer = df[df['infra_type'] == 'a_remplacer'].copy()
    df_reparer = df_reparer.drop_duplicates(subset=['id_batiment', 'infra_id']).reset_index(drop=True)
    # Nombre de bâtiments desservis par chaque infra
    nb_batiments_par_infra = df_reparer.groupby('infra_id')['id_batiment'].nunique()
    df_reparer = df_reparer.merge(nb_batiments_par_infra.rename('nb_batiments'), on='infra_id')
    df_reparer['difficulte_infra'] = df_reparer['longueur'] / df_reparer['nb_maisons']
    difficulte_batiments = (
        df_reparer.groupby('id_batiment')['difficulte_infra']
        .sum()
        .reset_index()
        .rename(columns={'difficulte_infra': 'difficulte_batiment'})
    )
    difficulte_batiments.head()

    # Étape 4 : Planification des réparations
    plan_df = planifier_reparations(df)


    
    print("PLANIFICATION TERMINÉE")
    print("=" * 60)

if __name__ == "__main__":
    main()