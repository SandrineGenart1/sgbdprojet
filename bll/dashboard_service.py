# bll/dashboard_service.py
from dataclasses import dataclass

from dal.repository import LocaMatRepository


@dataclass
class DashboardData:
    ca_30j: float
    contrats_actifs: int
    top5: list[tuple[str, float]]
    alertes: list[dict]


class DashboardService:
    """
    Service BLL pour le tableau de bord (page d'accueil).

    Rôle :
    - Orchestrer les appels à la DAL
    - Ne contient aucune requête SQL
    - Prépare des données directement affichables par l'UI
    """

    def __init__(self, repo: LocaMatRepository):
        self.repo = repo

    def get_dashboard(self) -> DashboardData:
        return DashboardData(
            ca_30j=self.repo.get_ca_30_jours(),
            contrats_actifs=self.repo.get_nb_contrats_actifs(),
            top5=self.repo.get_top5_rentabilite_mois(),
            alertes=self.repo.get_alertes_retard(),
        )
