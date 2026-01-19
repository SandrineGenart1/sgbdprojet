"""
Module catalogue_service.py
===========================

Couche BLL (Business Logic Layer).

Rôle :
- Orchestrer les cas d'usage (use cases) de l'application.
- Utiliser le Repository (DAL) pour accéder aux données.
- Appliquer les règles métier (plus tard : validations, exceptions métier, etc.).

Important (Option 1 : Injection de dépendance) :
- La BLL NE crée PAS de Session SQLAlchemy.
- La session est gérée à l’extérieur (UI / app Flask / scripts).
- On injecte donc un repository déjà prêt (qui lui-même contient la session).

Pourquoi c'est bien ?
- Tests plus faciles (on peut injecter un faux repo / repo de test).
- Architecture propre : UI -> BLL -> DAL -> DB
"""

from __future__ import annotations

from typing import List

from dal.models import Categorie, Marque, Modele, Materiel
from dal.repository import LocaMatRepository


class CatalogueService:
    """
    Service BLL pour tout ce qui concerne le catalogue :
    catégories, marques, modèles, matériels.
    """

    def __init__(self, repository: LocaMatRepository):
        """
        Injection de dépendance :
        on reçoit un repository (DAL) déjà construit.

        Le repository contient déjà une session SQLAlchemy.
        La BLL n'a pas à savoir comment la session est créée.
        """
        self.repo = repository

    def lister_categories(self) -> List[Categorie]:
        """
        Retourne la liste des catégories.
        (Le tri est fait côté DAL.)
        """
        return self.repo.get_all_categories()

    def lister_marques(self) -> List[Marque]:
        """
        Retourne la liste des marques.
        (Le tri est fait côté DAL.)
        """
        return self.repo.get_all_marques()

    def lister_modeles(self) -> List[Modele]:
        """
        Retourne la liste des modèles.
        """
        return self.repo.get_all_modeles()

    def lister_materiels_disponibles(self) -> List[Materiel]:
        """
        Retourne uniquement les matériels disponibles.

        Remarque :
        - Actuellement la règle 'Disponible' est appliquée dans le DAL
          via get_materiels_disponibles().
        - Si demain la règle change (ex: exclure 'Réservé'), on mettra
          la logique ici (BLL), et le DAL restera "bête" (requêtes).
        """
        return self.repo.get_materiels_disponibles()
