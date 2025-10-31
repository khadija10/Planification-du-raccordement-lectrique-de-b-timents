class Infra:
    """
    Représente une infrastructure électrique (ligne ou câble)
    reliée à un ou plusieurs bâtiments.
    """

    # Barèmes constants
    COUT_PAR_TYPE = {
        'aerien': 500,
        'semi-aerien': 750,
        'fourreau': 900
    }

    DUREE_PAR_TYPE = {
        'aerien': 2,          # heures / mètre
        'semi-aerien': 4,
        'fourreau': 5
    }

    COUT_OUVRIER_8H = 300
    MAX_OUVRIERS = 4

    def __init__(self, infra_id: str, length: float, infra_type: str,
                 nb_houses: int, type_infra: str):
        self.infra_id = infra_id
        self.length = float(length)
        self.infra_type = infra_type  # 'a_remplacer', 'infra_intacte', etc.
        self.nb_houses = int(nb_houses)
        self.type_infra = type_infra  # 'aerien', 'semi-aerien', 'fourreau'

        self.cout_par_m = self.COUT_PAR_TYPE.get(type_infra, 0)
        self.duree_par_m = self.DUREE_PAR_TYPE.get(type_infra, 0)

    # --- Méthodes principales ---
    def repair_infra(self):
        """Marque cette infrastructure comme réparée"""
        self.infra_type = "infra_intacte"

    def get_infra_cost(self) -> float:
        """Coût matériel"""
        return self.length * self.cout_par_m

    def get_infra_duration(self) -> float:
        """Durée théorique (h)"""
        return self.length * self.duree_par_m

    def __repr__(self):
        return (f"Infra({self.infra_id}, {self.length:.2f}m, {self.infra_type}, "
                f"type={self.type_infra}, {self.nb_houses} maisons, "
                f"coût_mat={self.get_infra_cost():.0f}€, "
                f"cout_total={self.get_total_cost():.0f}€, "
                f"durée={self.get_real_duration():.1f}h)")
