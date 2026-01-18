"""
Module catalogue_service.py
===========================

Couche BLL (Business Logic Layer).

Rôle :
- Orchestrer les cas d'usage (use cases) de l'application.
- Utiliser le Repository (DAL) pour accéder aux données.
- Ajouter des règles métier plus tard (validations, exceptions métier, etc.).

Important :
- La BLL ne fait pas de requêtes SQL/ORM directement.
- Elle délègue au repository.
- Idéalement, la BLL ne crée pas la session : elle reçoit ses dépendances.
  (=> injection de dépendance, plus simple à tester)
"""

from __future__ import annotations

from dal.repository import LocaMatRepository


class CatalogueService:
    """
    Service BLL pour tout ce qui concerne le catalogue
    (catégories, marques, modèles, matériels).

    Dans cette version "propre", le service reçoit un repository déjà prêt.
    Cela permet :
    - de ne pas dupliquer SessionLocal() partout
    - de tester la BLL facilement (en injectant un faux repository / mock)
    - de garder une architecture claire : UI -> BLL -> DAL
    """

    def __init__(self, repository: LocaMatRepository):
        """
        Injection de dépendance :
        on reçoit le repository (DAL) depuis l'extérieur.

        Args:
            repository (LocaMatRepository): repository configuré avec une session active
        """
        self.repository = repository

    def lister_categories(self):
        """
        Cas d'usage : lister les catégories.

        Ici, la BLL ne fait aucune requête :
        elle délègue au DAL, qui sait comment interroger la base.
        """
        return self.repository.get_all_categories()

    def lister_marques(self):
        """
        Cas d'usage : lister les marques.
        """
        return self.repository.get_all_marques()

    def lister_modeles(self):
        """
        Cas d'usage : lister les modèles.
        """
        return self.repository.get_all_modeles()

    def lister_materiels_disponibles(self):
        """
        Cas d'usage : lister les matériels disponibles.

        Remarque :
        - Aujourd'hui la règle "Disponible" est appliquée côté DAL.
        - Plus tard, si la règle évolue (ex : exclure aussi 'Réservé'),
          c'est typiquement la BLL qui portera la règle métier.
        """
        return self.repository.get_materiels_disponibles()
