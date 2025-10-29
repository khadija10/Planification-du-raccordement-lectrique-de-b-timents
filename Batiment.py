class Batiment:
    def __init__(self, id_building: str, list_infras: list):
        self.id_building = id_building
        self.list_infras = list_infras  # liste d’objets Infra

    def get_building_difficulty(self) -> float:
        """Somme des difficultés de ses infrastructures à réparer"""
        return sum(
            infra.get_infra_difficulty()
            for infra in self.list_infras
            if infra.infra_type == "a_remplacer"
        )
    
    def repair(self):
        """Répare toutes les infrastructures associées à ce bâtiment."""
        for infra in self.list_infras:
            infra.repair_infra()


    def __lt__(self, other):
        """Permet de trier les bâtiments selon leur difficulté"""
        return self.get_building_difficulty() < other.get_building_difficulty()

    def __repr__(self):
        return f"Batiment({self.id_building}, {len(self.list_infras)} infras, difficulté={self.get_building_difficulty():.2f})"
