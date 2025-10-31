class Batiment:
    """
    Représente un bâtiment relié à une ou plusieurs infrastructures.
    Version simplifiée :
    - Priorité métier : hôpital > école > habitation
    - Score = (coût total * durée totale) / nb_maisons
      → plus le score est faible, plus la réparation est efficace
    """

    PRIORITE_PAR_TYPE = {'hôpital': 1, 'école': 2, 'habitation': 3}

    def __init__(self, id_building: str, type_batiment: str, list_infras: list):
        self.id_building = id_building
        self.type_batiment = type_batiment.lower().strip()
        self.list_infras = list_infras
        self.last_score = 0

    # --- Métriques de base ---
    def get_building_houses(self) -> int:
        return sum(infra.nb_houses for infra in self.list_infras if infra.infra_type == "a_remplacer")

    def get_building_cost(self) -> float:
        """Coût matériel total"""
        return sum(infra.get_infra_cost() for infra in self.list_infras if infra.infra_type == "a_remplacer")

    def get_building_duration(self) -> float:
        """Durée théorique totale"""
        return sum(infra.get_infra_duration() for infra in self.list_infras if infra.infra_type == "a_remplacer")
   

    # --- Ratio priorité ---
    def get_priority_ratio(self) -> float:
        """Ratio = (coût total * durée réelle) / nb_maisons"""
        houses = self.get_building_houses() or 1
        ratio = (self.get_building_cost() * self.get_building_duration()) / houses
        self.last_score = ratio
        return ratio

    # --- Réparation ---
    def repair(self):
        for infra in self.list_infras:
            infra.repair_infra()

    # --- Comparaison / tri ---
    def __lt__(self, other):
        p1 = self.PRIORITE_PAR_TYPE.get(self.type_batiment, 4)
        p2 = self.PRIORITE_PAR_TYPE.get(other.type_batiment, 4)
        return (p1, self.last_score) < (p2, other.last_score)

    # --- Représentation lisible ---
    def __repr__(self):
        return (f"Batiment({self.id_building}, {self.type_batiment}, "
                f"{len(self.list_infras)} infras, coût_total={self.get_total_cost():,.0f}€, "
                f"durée_totale={self.get_real_duration():.1f}h, ratio={self.last_score:.3f})")
