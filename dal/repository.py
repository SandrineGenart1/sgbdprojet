"""
Module repository.py
====================

Couche DAL (Data Access Layer) - Pattern Repository.

Rôle :
- Contenir UNIQUEMENT la logique d'accès aux données (requêtes ORM).
- Aucune logique métier (pas de calcul de remise, pas de validation "VIP", etc.).
- Ne crée pas la session : elle est fournie par la couche BLL (Injection de dépendance).

Pourquoi ?
- Séparer clairement : UI -> BLL -> DAL -> DB
- Faciliter les tests (on peut injecter une session de test)
- Respecter l'architecture Repository + Unit of Work
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from dal.models import Client, Categorie, Marque, Modele, Materiel, Contrat, LigneContrat

from sqlalchemy.exc import IntegrityError



class LocaMatRepository:
    """
    Repository principal de l'application LOCA-MAT.

    Important :
    - self.session est une Session SQLAlchemy déjà ouverte (créée ailleurs).
    - Cette classe n'appelle jamais SessionLocal() : elle ne gère pas le cycle de vie.
    """

    def __init__(self, session: Session):
        """
        Injection de dépendance : on reçoit une session active.

        Args:
            session (Session): session SQLAlchemy ouverte par la BLL.
        """
        self.session = session

    # ----------------------------
    # A) LECTURES : CATALOGUE
    # ----------------------------

    def get_all_categories(self) -> list[Categorie]:
        """Retourne toutes les catégories (table CATEGORIE), triées par libellé."""
        stmt = select(Categorie).order_by(Categorie.cat_libelle)
        return self.session.execute(stmt).scalars().all()

    def get_all_marques(self) -> list[Marque]:
        """Retourne toutes les marques (table MARQUE), triées par libellé."""
        stmt = select(Marque).order_by(Marque.mar_libelle)
        return self.session.execute(stmt).scalars().all()

    def get_all_modeles(self) -> list[Modele]:
        """Retourne tous les modèles (table MODELE), triés par id."""
        stmt = select(Modele).order_by(Modele.mod_id)
        return self.session.execute(stmt).scalars().all()

    def get_all_materiels(self) -> list[Materiel]:
        """Retourne tout le matériel (table MATERIEL), trié par id."""
        stmt = select(Materiel).order_by(Materiel.mat_id)
        return self.session.execute(stmt).scalars().all()

    def get_materiel_by_id(self, mat_id: int) -> Materiel | None:
        """Retourne un matériel par son ID, ou None s'il n'existe pas."""
        stmt = select(Materiel).where(Materiel.mat_id == mat_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_client_by_id(self, cli_id: int) -> Client | None:
        """Retourne un client par son ID, ou None s'il n'existe pas."""
        stmt = select(Client).where(Client.cli_id == cli_id)
        return self.session.execute(stmt).scalar_one_or_none()
    def get_contrats_by_client(self, cli_id: int) -> list[Contrat]:
        """
        Retourne tous les contrats d'un client, triés du plus récent au plus ancien.

        Args:
            cli_id (int): identifiant du client
        """
        stmt = (
            select(Contrat)
            .where(Contrat.cli_id == cli_id)
            .order_by(Contrat.cont_id.desc())
        )
        return self.session.execute(stmt).scalars().all()
    
    def get_lignes_by_contrat(self, cont_id: int) -> list[LigneContrat]:
        """
        Retourne les lignes d'un contrat (matériels loués), triées par id.

        Args:
            cont_id (int): identifiant du contrat
        """
        stmt = (
            select(LigneContrat)
            .where(LigneContrat.cont_id == cont_id)
            .order_by(LigneContrat.lc_id)
        )
        return self.session.execute(stmt).scalars().all()
    
    def get_materiels_disponibles(self) -> list[Materiel]:
        """
        Retourne les matériels dont le statut est 'Disponible'.

        Utile pour afficher la liste des matériels louables.
        """
        stmt = (
            select(Materiel)
            .where(Materiel.mat_statut == "Disponible")
            .order_by(Materiel.mat_id)
        )
        return self.session.execute(stmt).scalars().all()
    def add_client(self, client: Client) -> Client:
        """
        Ajoute un client en base de données.

        Rôle DAL :
        - ajouter l'objet à la session
        - faire commit
        - en cas d'erreur d'intégrité (email unique, etc.), rollback et relancer

        Args:
            client (Client): objet Client ORM à insérer

        Returns:
            Client: le client inséré (avec cli_id rempli après commit)
        """
        try:
            self.session.add(client)
            self.session.commit()
            # Optionnel : rafraîchir l'objet pour récupérer les valeurs générées (cli_id)
            self.session.refresh(client)
            return client
        except IntegrityError:
            self.session.rollback()
            raise
    


    def louer_materiel(self, mat_id: int) -> bool:
        """
        Tente de louer un matériel (logique simple testable avec mocking).

        But :
        - illustrer un test unitaire "pur" (sans DB) grâce au mock d'une session.

        Règles :
        - Si le matériel n'existe pas -> False
        - Si son statut n'est pas 'Disponible' -> False
        - Sinon : on passe le statut à 'Loué', on commit, et on renvoie True

        Args:
            mat_id (int): identifiant du matériel à louer

        Returns:
            bool: True si la location est effectuée, False sinon
        """
        # session.get(Model, id) = accès direct par clé primaire (facile à mocker)
        materiel = self.session.get(Materiel, mat_id)

        # 1) Le matériel n'existe pas
        if materiel is None:
            return False

        # 2) Le matériel existe mais n'est pas louable
        if materiel.mat_statut != "Disponible":
            return False

        # 3) Cas nominal : on loue
        materiel.mat_statut = "Loué"
        self.session.commit()
        return True

