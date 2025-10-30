import pandas as pd

def update_reseau_excel():
    print("MISE À JOUR DU FICHIER 'reseau_en_arbre.xlsx'")
    print("=" * 60)

    try:
        batiments_df = pd.read_csv('batiments.csv')
        infra_df = pd.read_csv('infra.csv')
        reseau_df = pd.read_excel('reseau_en_arbre.xlsx')
    except Exception as e:
        print(f"Erreur de lecture des fichiers : {e}")
        return

    print(f"Bâtiments chargés : {len(batiments_df)}")
    print(f"Infrastructures chargées : {len(infra_df)}")
    print(f"Entrées réseau : {len(reseau_df)}\n")

    # Fusion avec batiments.csv
    reseau_df = reseau_df.merge(
        batiments_df[['id_batiment', 'type_batiment', 'nb_maisons']],
        on='id_batiment', how='left', suffixes=('', '_new')
    )
    reseau_df['nb_maisons'] = reseau_df['nb_maisons_new'].combine_first(reseau_df['nb_maisons'])
    reseau_df.drop(columns=['nb_maisons_new'], inplace=True)

    # Fusion avec infra.csv
    reseau_df = reseau_df.merge(
        infra_df[['id_infra', 'type_infra']],
        left_on='infra_id', right_on='id_infra', how='left'
    ).drop(columns=['id_infra'])

    # Vérification des correspondances
    missing_bat = reseau_df['type_batiment'].isna().sum()
    missing_infra = reseau_df['type_infra'].isna().sum()
    print(f"Bâtiments sans correspondance : {missing_bat}")
    print(f"Infrastructures sans correspondance : {missing_infra}\n")

    # Réorganisation des colonnes
    columns_order = [
        'id_batiment', 'type_batiment', 'nb_maisons',
        'infra_id', 'infra_type', 'type_infra', 'longueur'
    ]
    reseau_df = reseau_df[columns_order]

    # Sauvegarde du nouveau fichier Excel
    output_file = 'reseau_en_arbre_updated.xlsx'
    reseau_df.to_excel(output_file, index=False)

    print(f"Fichier mis à jour et sauvegardé sous : {output_file}")
    print("=" * 60)
    print("Aperçu :")
    print(reseau_df.head(), "\n")

    # Petites stats
    print("Résumé par type de bâtiment :")
    print(reseau_df['type_batiment'].value_counts(), "\n")
    print("Résumé par type d’infrastructure :")
    print(reseau_df['type_infra'].value_counts(), "\n")

    return reseau_df

if __name__ == "__main__":
    update_reseau_excel()
