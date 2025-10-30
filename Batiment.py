import networkx as nx
import pandas as pd

class Batiment:
    """
    Représente un bâtiment connecté à une ou plusieurs infrastructures.
    Priorisation basée sur la difficulté, le coût, la durée et la mutualisation du réseau.
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
        self.last_score = 0  # score utilisé pour le tri et affichage

    # --- Métriques principales ---
    def get_building_difficulty(self) -> float:
        return sum(infra.get_infra_difficulty() for infra in self.list_infras if infra.infra_type == "a_remplacer")

    def get_building_cost(self) -> float:
        return sum(infra.get_infra_cost() for infra in self.list_infras if infra.infra_type == "a_remplacer")

    def get_building_duration(self) -> float:
        return sum(infra.get_infra_duration() for infra in self.list_infras if infra.infra_type == "a_remplacer")

    # --- Réparation ---
    def repair(self):
        for infra in self.list_infras:
            infra.repair_infra()

    # --- Mutualisation réseau ---
    def get_mutualisation_score(self, G: nx.Graph) -> float:
        return 1 + G.degree(self.id_building)

    # --- Score de priorité basé sur le graphe ---
    def get_priority_score_graph(self, G: nx.Graph) -> float:
        """
        Score de priorité avancé :
        Combine la structure du graphe (mutualisation, coût, difficulté)
        avec la criticité du type de bâtiment (PRIORITE_PAR_TYPE).
        Les hôpitaux sont traités avant les écoles, puis les habitations.
        """

        # --- 1. Sélection des infrastructures à remplacer ---
        infras_remplacer = [infra for infra in self.list_infras if infra.infra_type == "a_remplacer"]
        if not infras_remplacer:
            self.last_score = 0
            return 0

        # --- 2. Indicateurs techniques ---
        total_cost = sum(infra.get_infra_cost() for infra in infras_remplacer)
        total_difficulty = sum(infra.get_infra_difficulty() for infra in infras_remplacer)
        total_houses = sum(infra.nb_houses for infra in infras_remplacer)

        avg_difficulty = total_difficulty / len(infras_remplacer)
        efficacite = total_houses / (total_cost + 1)
        facilite = 1 / (1 + avg_difficulty)
        mutualisation = self.get_mutualisation_score(G)

        score_technique = efficacite * facilite * mutualisation

        # --- 3. Facteur de priorité basé sur le type ---
        # (plus le nombre est petit, plus la priorité est haute)
        base_priorite = self.PRIORITE_PAR_TYPE.get(self.type_batiment, 4)

        # --- 4. Combinaison hiérarchisée ---
        # On inverse la logique pour que les plus prioritaires (hôpital=1)
        # aient un score global plus élevé
        score_final = ((4 - base_priorite) * 1e6) + (score_technique * 1e6)

        self.last_score = score_final
        return score_final

    def get_priority_score_graph_optimal(self, repaired_infras: set, G: nx.Graph = None) -> float:
        """
        Score d'optimalité pour choix glouton :
        - calcule les valeurs marginales si on répare ce bâtiment *maintenant* en tenant compte
        des infrastructures déjà réparées (repaired_infras).
        - utilise : prises supplémentaires (nb_houses), coût marginal, mutualisation (degré dans G),
        et la priorité métier (hôpital/école/habitation).
        - renvoie un score : plus élevé = prioritaire.
        """
        # infrastructures réellement à remplacer et pas encore réparées
        infras_a_considerer = [
            infra for infra in self.list_infras
            if infra.infra_type == "a_remplacer" and infra.infra_id not in repaired_infras
        ]

        if not infras_a_considerer:
            self.last_score = 0.0
            return 0.0

        # marginals
        marginal_cost = sum(infra.get_infra_cost() for infra in infras_a_considerer)
        marginal_houses = sum(infra.nb_houses for infra in infras_a_considerer)
        marginal_difficulty = sum(infra.get_infra_difficulty() for infra in infras_a_considerer)
        marginal_duration = sum(infra.get_infra_duration() for infra in infras_a_considerer)

        # sécurité
        eps = 1e-6

        # efficacité (prises raccordées par euro dépensé)
        efficacite = marginal_houses / (marginal_cost + eps)

        # facteur "facilité" (on favorise interventions pas trop difficiles)
        # la plus faible difficulté => plus favorable
        if len(infras_a_considerer) > 0:
            avg_difficulty = marginal_difficulty / len(infras_a_considerer)
        else:
            avg_difficulty = 0.0
        facilite = 1.0 / (1.0 + avg_difficulty)

        # mutualisation : si noeud fortement connecté, réparer ici peut profiter plus au réseau
        mutualisation = 1.0
        if G is not None and self.id_building in G:
            mutualisation += G.degree(self.id_building)

        # priorité métier : on veut que hôpital>école>habitation
        base_priorite = self.PRIORITE_PAR_TYPE.get(self.type_batiment, 4)

        # Compose a score:
        # - priorité métier a poids très élevé (pour garantir ordre hiérarchique)
        # - puis efficacite * facilite * mutualisation comme critère économique/réseau
        # - on pénalise légèrement le coût marginal et la durée marginale pour départager égalités
        score_economique = efficacite * facilite * mutualisation

        # pondérations (échelles choisies pour garder priorité métier dominante)
        score_final = ((4 - base_priorite) * 1e6) + (score_economique * 1e5) \
                    - (marginal_cost * 1e-2) - (marginal_duration * 1e2)

        # conserver les valeurs pour debug/affichage
        self.last_score = score_final
        # on peut aussi stocker des métriques utiles si besoin (facultatif)
        self._optimal_marginal = {
            "marginal_cost": marginal_cost,
            "marginal_houses": marginal_houses,
            "marginal_duration": marginal_duration,
            "marginal_difficulty": marginal_difficulty,
            "score_economique": score_economique
        }

        return score_final

    

    # --- Comparaison et affichage ---
    def __lt__(self, other):
        # Priorité métier : hôpital > école > habitation
        p1 = self.PRIORITE_PAR_TYPE.get(self.type_batiment, 4)
        p2 = self.PRIORITE_PAR_TYPE.get(other.type_batiment, 4)

        # Si le type diffère → ordre de priorité
        if p1 != p2:
            return p1 < p2

        # Sinon, on trie par score décroissant
        return self.last_score > other.last_score

    def __repr__(self):
        return (f"Batiment({self.id_building}, type={self.type_batiment}, "
                f"{len(self.list_infras)} infras, difficulté={self.get_building_difficulty():.2f}, "
                f"coût={self.get_building_cost():.0f}€, durée={self.get_building_duration():.1f}h, "
                f"score={self.last_score:.2f})")
