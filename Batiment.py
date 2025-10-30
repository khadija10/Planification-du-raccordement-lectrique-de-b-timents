import networkx as nx

class Batiment:
    """
    Représente un bâtiment connecté à une ou plusieurs infrastructures.
    Inclut une logique de priorisation basée sur la difficulté, le coût,
    la durée et la mutualisation du réseau électrique.
    """

    PRIORITE_PAR_TYPE = {
        'hôpital': 1,
        'école': 2,
        'habitation': 3
    }

    def __init__(self, id_building: str, type_batiment: str, list_infras: list):
        self.id_building = id_building
        self.type_batiment = type_batiment.lower().strip()
        self.list_infras = list_infras  # liste d’objets Infra

    # --- Métriques principales ---

    def get_building_difficulty(self) -> float:
        """Somme des difficultés des infras à remplacer"""
        return sum(
            infra.get_infra_difficulty()
            for infra in self.list_infras
            if infra.infra_type == "a_remplacer"
        )

    def get_building_cost(self) -> float:
        """Somme des coûts totaux des infras à remplacer"""
        return sum(
            infra.get_infra_cost()
            for infra in self.list_infras
            if infra.infra_type == "a_remplacer"
        )

    def get_building_duration(self) -> float:
        """Somme des durées totales des infras à remplacer"""
        return sum(
            infra.get_infra_duration()
            for infra in self.list_infras
            if infra.infra_type == "a_remplacer"
        )

    # --- Gestion du statut ---

    def repair(self):
        """Répare toutes les infrastructures associées à ce bâtiment."""
        for infra in self.list_infras:
            infra.repair_infra()

    # --- Fonctions de tri et priorité (ancienne méthode basique) ---

    def get_priority_score(self) -> float:
        """
        Score de priorité global :
        Priorité par type de bâtiment
        Sous-score par difficulté, coût et durée
        Moins le score est élevé, plus le bâtiment est prioritaire.
        """
        priority_base = self.PRIORITE_PAR_TYPE.get(self.type_batiment, 4)

        diff = self.get_building_difficulty()
        cout = self.get_building_cost()
        duree = self.get_building_duration()

        sub_score = (diff * 0.5) + (cout * 0.3 / 1000) + (duree * 0.2 / 10)
        return priority_base * 10000 + sub_score

    # --- Nouvelle logique basée sur la théorie des graphes ---

    def get_mutualisation_score(self, G: nx.Graph) -> float:
        """
        Score basé sur le degré de connexion du bâtiment (mutualisation).
        Plus un bâtiment est connecté à d'autres nœuds, plus il bénéficie
        d'une mutualisation favorable.
        """
        return 1 + G.degree(self.id_building)

    def get_priority_score_graph(self, G: nx.Graph) -> float:
        """
        Métrique de priorisation avancée :
        Combine coût total, difficulté moyenne, mutualisation du réseau et type du bâtiment.
        Favorise les bâtiments peu coûteux et bien mutualisés.
        """
        priority_base = self.PRIORITE_PAR_TYPE.get(self.type_batiment, 4)

        infras_remplacer = [
            infra for infra in self.list_infras if infra.infra_type == "a_remplacer"
        ]
        if not infras_remplacer:
            return float('inf')

        total_cost = sum(infra.get_infra_cost() for infra in infras_remplacer)
        total_difficulty = sum(infra.get_infra_difficulty() for infra in infras_remplacer)
        total_houses = sum(infra.nb_houses for infra in infras_remplacer)

        avg_difficulty = total_difficulty / len(infras_remplacer)
        efficacite = total_houses / (total_cost + 1)
        facilite = 1 / (1 + avg_difficulty)
        mutualisation = self.get_mutualisation_score(G)

        # Combinaison pondérée des critères
        score_utilite = efficacite * facilite * mutualisation
        score_final = (10 / priority_base) * score_utilite * 1e6

        return score_final

    # --- Comparaison et affichage ---

    def __lt__(self, other):
        """Permet de trier les bâtiments selon leur score de priorité"""
        return self.get_priority_score() < other.get_priority_score()

    def __repr__(self):
        return (f"Batiment({self.id_building}, "
                f"type={self.type_batiment}, "
                f"{len(self.list_infras)} infras, "
                f"difficulté={self.get_building_difficulty():.2f}, "
                f"coût={self.get_building_cost():.0f}€, "
                f"durée={self.get_building_duration():.1f}h, "
                f"score={self.get_priority_score():.2f})")
