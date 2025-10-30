class Batiment:
    """
    Représente un bâtiment connecté à une ou plusieurs infrastructures.
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

    # --- Fonctions de tri et priorité ---

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

        # Sous-score interne : équilibre entre trois critères
        sub_score = (diff * 0.5) + (cout * 0.3 / 1000) + (duree * 0.2 / 10)

        # Poids fort pour séparer les catégories de bâtiments
        return priority_base * 10000 + sub_score


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
