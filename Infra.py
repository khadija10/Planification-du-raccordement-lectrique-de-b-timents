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

    def __init__(self, infra_id: str, length: float, infra_type: str,
                 nb_houses: int, type_infra: str):
        self.infra_id = infra_id
        self.length = float(length)
        self.infra_type = infra_type  # 'a_remplacer', 'infra_intacte', etc.
        self.nb_houses = int(nb_houses)
        self.type_infra = type_infra  # 'aerien', 'semi-aerien', 'fourreau'

        # Coût et durée unitaires dérivés du type_infra
        self.cout_par_m = self.COUT_PAR_TYPE.get(type_infra, 0)
        self.duree_par_m = self.DUREE_PAR_TYPE.get(type_infra, 0)

    # --- Méthodes principales ---

    def repair_infra(self):
        """Marque cette infrastructure comme réparée"""
        self.infra_type = "infra_intacte"

    def get_infra_difficulty(self) -> float:
        """Retourne la difficulté (rapport longueur / nb maisons)"""
        if self.nb_houses == 0:
            return float('inf')
        return self.length / self.nb_houses

    def get_infra_cost(self) -> float:
        """Retourne le coût total (longueur × coût/m)"""
        return self.length * self.cout_par_m

    def get_infra_duration(self) -> float:
        """Retourne la durée totale (longueur × durée/m)"""
        return self.length * self.duree_par_m

    # --- Opérateurs utiles ---

    def __radd__(self, other):
        """Permet de sommer les difficultés (ex : sum(list_infras))"""
        if isinstance(other, (int, float)):
            return other + self.get_infra_difficulty()
        return NotImplemented

    def __repr__(self):
        return (f"Infra({self.infra_id}, {self.length:.2f}m, "
                f"{self.infra_type}, type={self.type_infra}, "
                f"{self.nb_houses} maisons, "
                f"coût={self.get_infra_cost():.0f}€, "
                f"durée={self.get_infra_duration():.1f}h)")
