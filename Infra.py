class Infra:
    def __init__(self, infra_id: str, length: float, infra_type: str, nb_houses: int):
        self.infra_id = infra_id
        self.length = float(length)
        self.infra_type = infra_type
        self.nb_houses = int(nb_houses)

    def repair_infra(self):
        """Marque cette infrastructure comme réparée"""
        self.infra_type = "infra_intacte"

    def get_infra_difficulty(self) -> float:
        """Retourne la difficulté de cette infrastructure"""
        if self.nb_houses == 0:
            return float('inf')
        return self.length / self.nb_houses

    def __radd__(self, other):
        """Permet de sommer les difficultés"""
        if isinstance(other, (int, float)):
            return other + self.get_infra_difficulty()
        return NotImplemented

    def __repr__(self):
        return f"Infra({self.infra_id}, {self.length:.2f}m, {self.infra_type}, {self.nb_houses} maisons)"
