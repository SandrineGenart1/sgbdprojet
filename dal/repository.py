"""
Module repository.py
====================

Couche DAL (Data Access Layer) - Pattern Repository.

Rôle :
- Contenir UNIQUEMENT la logique d'accès aux données (requêtes ORM).
- Aucune logique métier (pas de calcul, pas de règles applicatives).
- Ne crée PAS la session : elle est fournie par la couche supérieure (BLL / UI).

Architecture respectée :
UI (Flask) → BLL (services) → DAL (repository) → Base de données
"""

from __future__ import annotations

# SQLAlchemy
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError

# Modèles ORM
from dal.models import (
    Client,
    Categorie,
    Marque,
    Modele,
    Materiel,
    Contrat,
    LigneContrat,
)


class LocaMatRepository:
    """
    Repository principal de l'application LOCA-MAT.

    Important :
    - self.session est une Session SQLAlchemy déjà ouverte.
    - Cette classe NE DOIT PAS ouvrir ou fermer la session.
    """

    def __init__(self, session: Session):
        """
        Injection de dépendance :
        le repository reçoit une session existante.

        Args:
            session (Session): session SQLAlchemy ouverte
        """
        self.session = session

    # ======================================================
    # A) LECTURES : CATALOGUE
    # ======================================================

    def get_all_categories(self) -> list[Categorie]:
        """Retourne toutes les catégories, triées par libellé."""
        stmt = select(Categorie).order_by(Categorie.cat_libelle)
        return self.session.execute(stmt).scalars().all()

    def get_all_marques(self) -> list[Marque]:
        """Retourne toutes les marques, triées par libellé."""
        stmt = select(Marque).order_by(Marque.mar_libelle)
        return self.session.execute(stmt).scalars().all()

    def get_all_modeles(self) -> list[Modele]:
        """Retourne tous les modèles."""
        stmt = select(Modele).order_by(Modele.mod_id)
        return self.session.execute(stmt).scalars().all()

    def get_all_materiels(self) -> list[Materiel]:
        """Retourne tout le matériel."""
        stmt = select(Materiel).order_by(Materiel.mat_id)
        return self.session.execute(stmt).scalars().all()

    def get_materiel_by_id(self, mat_id: int) -> Materiel | None:
        """Retourne un matériel par son ID."""
        stmt = select(Materiel).where(Materiel.mat_id == mat_id)
        return self.session.execute(stmt).scalar_one_or_none()

    # ======================================================
    # B) RELATIONS MÉTIER
    # ======================================================

    def get_contrats_by_client(self, cli_id: int) -> list[Contrat]:
        """Retourne les contrats d'un client."""
        stmt = (
            select(Contrat)
            .where(Contrat.cli_id == cli_id)
            .order_by(Contrat.cont_id.desc())
        )
        return self.session.execute(stmt).scalars().all()

    def get_lignes_by_contrat(self, cont_id: int) -> list[LigneContrat]:
        """Retourne les lignes d'un contrat."""
        stmt = (
            select(LigneContrat)
            .where(LigneContrat.cont_id == cont_id)
            .order_by(LigneContrat.lc_id)
        )
        return self.session.execute(stmt).scalars().all()

    # ======================================================
    # C) CAS IMPORTANT POUR FLASK / JINJA
    # ======================================================

    def get_materiels_disponibles(self) -> list[Materiel]:
        """
        Retourne les matériels dont le statut est 'Disponible'.

        ⚠️ PROBLÈME CLASSIQUE AVEC FLASK/JINJA :
        - Le template accède à des relations ORM :
          materiel.modele.marque.cat_libelle
        - MAIS la session est fermée après le `with SessionLocal()`
        - Donc SQLAlchemy ne peut plus charger les relations (lazy loading)
        → ERREUR : DetachedInstanceError

        ✅ SOLUTION :
        Charger les relations AVANT de quitter la session
        grâce au *eager loading* (selectinload).
        """

        stmt = (
            select(Materiel)

            # Chargement anticipé des relations nécessaires au template
            .options(
                selectinload(Materiel.modele)
                .selectinload(Modele.marque),

                selectinload(Materiel.modele)
                .selectinload(Modele.categorie),
            )

            .where(Materiel.mat_statut == "Disponible")
            .order_by(Materiel.mat_id)
        )

        return self.session.execute(stmt).scalars().all()

    # ======================================================
    # D) INSERTIONS
    # ======================================================

    def add_client(self, client: Client) -> Client:
        """
        Ajoute un client en base.

        Gestion propre :
        - commit si OK
        - rollback en cas d'erreur d'intégrité
        """
        try:
            self.session.add(client)
            self.session.commit()
            self.session.refresh(client)
            return client
        except IntegrityError:
            self.session.rollback()
            raise

    # ======================================================
    # E) EXEMPLE MÉTIER SIMPLE (MOCKABLE)
    # ======================================================

    def louer_materiel(self, mat_id: int) -> bool:
        """
        Exemple de logique simple testable avec mocking.

        Règles :
        - matériel inexistant → False
        - matériel non disponible → False
        - sinon → passe à 'Loué' et commit
        """

        materiel = self.session.get(Materiel, mat_id)

        if materiel is None:
            return False

        if materiel.mat_statut != "Disponible":
            return False

        materiel.mat_statut = "Loué"
        self.session.commit()
        return True
