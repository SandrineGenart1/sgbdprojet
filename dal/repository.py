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

#Bibliothèque standard Python
from datetime import date, timedelta

# SQLAlchemy
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, desc


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
    
    def get_all_clients(self) -> list[Client]:
        """
        Retourne tous les clients, triés par nom puis prénom.
        Utile pour proposer une liste de clients dans l'UI (formulaire de location).
        """
        stmt = select(Client).order_by(Client.cli_nom, Client.cli_prenom)
        return self.session.execute(stmt).scalars().all()

    def get_materiels_by_ids(self, mat_ids: list[int]) -> list[Materiel]:
        """
        Retourne une liste de matériels correspondant à une liste d'IDs.

        Important :
        - Lecture simple (pas de verrou).
        - L'ordre retourné n'est pas garanti.
        """
        if not mat_ids:
            return []

        stmt = select(Materiel).where(Materiel.mat_id.in_(mat_ids))
        return self.session.execute(stmt).scalars().all()

    def get_materiels_by_ids_for_update(self, mat_ids: list[int]) -> list[Materiel]:
        """
        Retourne une liste de matériels correspondant à une liste d'IDs,
        en appliquant un verrou pessimiste (FOR UPDATE).

        À utiliser uniquement dans une transaction (with session.begin()).
        """
        if not mat_ids:
            return []

        stmt = (
            select(Materiel)
            .where(Materiel.mat_id.in_(mat_ids))
            .with_for_update()
        )
        return self.session.execute(stmt).scalars().all()


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
    


    def get_all_contrats(self) -> list[Contrat]:
        """Retourne tous les contrats avec client + lignes + matériel (pour affichage UI)."""
        stmt = (
            select(Contrat)
            .options(
                selectinload(Contrat.client),
                selectinload(Contrat.lignes).selectinload(LigneContrat.materiel)
            )
            .order_by(Contrat.cont_id.desc())
        )
        return self.session.execute(stmt).scalars().all()



    
    def client_est_risque(self, cli_id: int) -> bool:
        """
        Retourne True si le client a rendu en retard lors de sa dernière location.

        Définition retenue :
        - on prend le dernier contrat du client (cont_id le plus grand)
        - si au moins une ligne a une date de retour réelle > date prévue => risque
        """
        # 1) Dernier contrat
        stmt_contrat = (
            select(Contrat)
            .where(Contrat.cli_id == cli_id)
            .order_by(Contrat.cont_id.desc())
            .limit(1)
        )
        dernier_contrat = self.session.execute(stmt_contrat).scalar_one_or_none()

        if dernier_contrat is None:
            return False  # jamais loué => pas "à risque"

        # 2) Lignes du dernier contrat
        lignes = self.get_lignes_by_contrat(dernier_contrat.cont_id)

        for lc in lignes:
            if lc.lc_dateretourreelle is not None and lc.lc_dateretourreelle > lc.lc_dateretourprevue:
                return True

        return False


    # ======================================================
    # C) CAS IMPORTANT POUR FLASK / JINJA
    # ======================================================

    def get_materiels_disponibles(self) -> list[Materiel]:
        """
        Retourne les matériels dont le statut est 'Disponible'.

         PROBLÈME CLASSIQUE AVEC FLASK/JINJA :
        - Le template accède à des relations ORM :
          materiel.modele.marque.cat_libelle
        - MAIS la session est fermée après le `with SessionLocal()`
        - Donc SQLAlchemy ne peut plus charger les relations (lazy loading)
        → ERREUR : DetachedInstanceError

        SOLUTION :
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
    # E) EXEMPLE MÉTIER (MOCKABLE)
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


     # ======================================================
    # F) LOCATIONS (TRANSACTION)
    # ======================================================

    def transaction_valider_location(
        self,
        client_id: int,
        materiel_ids: list[int],
        date_debut,
        date_fin,
        nb_jours: int,
        pricing_callback,
    ):
        """
        Valide une location de manière atomique.

        Étape B1 :
        - démarrer une transaction
        - vérifier que le client existe
        - verrouiller les matériels (FOR UPDATE)
        - vérifier qu'ils existent tous
        - vérifier qu'ils sont tous 'Disponible'

        Étapes suivantes (B2, B3, ...) :
        - calcul du prix (mat_prix_jour * nb_jours + remises/surcharge)
        - création Contrat + Lignes
        - mise à jour statut => 'Loué'
        """

        if not materiel_ids:
            raise ValueError("Aucun matériel sélectionné.")

        with self.session.begin():

            # 1) Client existe ?
            client = self.session.get(Client, client_id)
            if client is None:
                raise ValueError("Client introuvable.")

            # 2) Verrouillage matériels (concurrence)
            materiels = self.get_materiels_by_ids_for_update(materiel_ids)

            # 3) Tous les IDs existent ?
            ids_trouves = {m.mat_id for m in materiels}
            ids_demandes = set(materiel_ids)
            ids_manquants = ids_demandes - ids_trouves
            if ids_manquants:
                raise ValueError(f"Matériel(s) introuvable(s) : {sorted(ids_manquants)}")

            # 4) Tous disponibles ?
            non_dispos = [m for m in materiels if m.mat_statut != "Disponible"]
            if non_dispos:
                ids_non_dispos = [m.mat_id for m in non_dispos]
                raise ValueError(
                    "Stock insuffisant : un ou plusieurs matériels ne sont plus disponibles "
                    f"(IDs: {ids_non_dispos})."
                )

            # 5) Calcul du total de base (prix/jour * nb_jours)
            # mat_prix_jour est un Numeric => souvent un Decimal
            total_base = sum((m.mat_prix_jour * nb_jours) for m in materiels)

            # 6) Déterminer si le client est "à risque"
            client_risque = self.client_est_risque(client_id)

            # 7) Appeler la BLL via le callback (remise durée, VIP, risque)
            if pricing_callback is None:
                raise ValueError("pricing_callback manquant (la BLL doit fournir calculer_prix).")

            prix_detail = pricing_callback(
                total_base=float(total_base),
                nb_jours=nb_jours,
                client_vip=bool(client.cli_vip),
                client_risque=client_risque
            )

            # 8) Création du contrat
            contrat = Contrat(
                cont_dateDebut=date_debut,
                cont_dateFin=date_fin,
                cli_id=client_id
            )
            self.session.add(contrat)
            self.session.flush()  # force l'INSERT pour obtenir cont_id

            # 9) Création des lignes de contrat (1 ligne par matériel)
            for m in materiels:
                ligne = LigneContrat(
                    lc_dateretourprevue=date_fin,
                    lc_dateretourreelle=None,
                    cont_id=contrat.cont_id,
                    mat_id=m.mat_id
                )
                self.session.add(ligne)

            # 10) Mise à jour des statuts -> 'Loué'
            for m in materiels:
                m.mat_statut = "Loué"

            return contrat, materiels, prix_detail


    # ======================================================
    # G) TABLEAU DE BORD (AGREGATIONS SQL)
    # ======================================================
    # A. Chiffre d’affaires 30 jours

    def get_ca_30_jours(self) -> float:
        date_limite = date.today() - timedelta(days=30)

        # durée en jours = (dateFin - dateDebut + 1)
        # En PostgreSQL, (cont_datefin - cont_datedebut) renvoie un intervalle/jours selon types.
        # Avec DATE, ça renvoie un integer (nb jours).
        duree = (Contrat.cont_dateFin - Contrat.cont_dateDebut + 1)

        stmt = (
            select(func.coalesce(func.sum(Materiel.mat_prix_jour * duree), 0.0))
            .select_from(Contrat)
            .join(LigneContrat, LigneContrat.cont_id == Contrat.cont_id)
            .join(Materiel, Materiel.mat_id == LigneContrat.mat_id)
            .where(Contrat.cont_dateDebut >= date_limite)
        )

        return float(self.session.execute(stmt).scalar_one())


    # Top 5 rentabilité du mois

    def get_top5_rentabilite_mois(self) -> list[tuple[str, float]]:

        debut_mois = date.today().replace(day=1)
        duree = (Contrat.cont_dateFin - Contrat.cont_dateDebut + 1)

        stmt = (
            select(
                Modele.mod_libelle,
                Marque.mar_libelle,
                func.coalesce(func.sum(Materiel.mat_prix_jour * duree), 0.0).label("total")
            )
            .select_from(Contrat)
            .join(LigneContrat, LigneContrat.cont_id == Contrat.cont_id)
            .join(Materiel, Materiel.mat_id == LigneContrat.mat_id)
            .join(Modele, Modele.mod_id == Materiel.mod_id)
            .join(Marque, Marque.mar_id == Modele.mar_id)
            .where(Contrat.cont_dateDebut >= debut_mois)
            .group_by(Modele.mod_libelle, Marque.mar_libelle)
            .order_by(desc("total"))
            .limit(5)
        )

        rows = self.session.execute(stmt).all()
        return [(f"{mar} {mod}", float(total)) for (mod, mar, total) in rows]


    # C. Alertes retard (articles non restitués + date prévue dépassée)

    def get_alertes_retard(self) -> list[dict]:
        from datetime import date

        stmt = (
            select(
                Client.cli_nom,
                Client.cli_prenom,
                Client.cli_mail,
                Materiel.mat_id,
                Materiel.mat_serial,
                LigneContrat.lc_dateretourprevue
            )
            .select_from(LigneContrat)
            .join(Contrat, Contrat.cont_id == LigneContrat.cont_id)
            .join(Client, Client.cli_id == Contrat.cli_id)
            .join(Materiel, Materiel.mat_id == LigneContrat.mat_id)
            .where(LigneContrat.lc_dateretourreelle.is_(None))
            .where(LigneContrat.lc_dateretourprevue < date.today())
            .order_by(LigneContrat.lc_dateretourprevue.asc())
        )

        rows = self.session.execute(stmt).all()
        return [
            {
                "client_nom": nom,
                "client_prenom": prenom,
                "client_mail": mail,
                "mat_id": mat_id,
                "mat_serial": serial,
                "retour_prevu": retour_prevu,
            }
            for (nom, prenom, mail, mat_id, serial, retour_prevu) in rows
        ]


    # D. Contrats actifs

    def get_nb_contrats_actifs(self) -> int:
        from datetime import date
        stmt = (
            select(func.count(Contrat.cont_id))
            .where(Contrat.cont_dateDebut <= date.today())
            .where(Contrat.cont_dateFin >= date.today())
        )
        return int(self.session.execute(stmt).scalar_one())

    # ======================================================
    # H) RESTITUTIONS
    # ======================================================

    def get_lignes_a_restituer(self) -> list[LigneContrat]:
        """
        Lignes non restituées (retour réel = NULL).
        Sert à afficher une liste à l'écran / pour les tests.
        """
        stmt = (
            select(LigneContrat)
            .options(
                selectinload(LigneContrat.contrat).selectinload(Contrat.client),
                selectinload(LigneContrat.materiel),
            )
            .where(LigneContrat.lc_dateretourreelle.is_(None))
            .order_by(LigneContrat.lc_dateretourprevue.asc())
        )
        return self.session.execute(stmt).scalars().all()
    

    def transaction_restituer_lignes(self, lc_ids: list[int], date_retour_reelle: date):
        """
        Restitution atomique :
        - verrouille les lignes + matériels
        - renseigne la date de retour réelle
        - calcule retard + pénalité
        - remet le statut matériel à 'Disponible'
        """
        if not lc_ids:
            raise ValueError("Aucune ligne sélectionnée.")

        # Important (SQLAlchemy 2.0) :
        # un SELECT avant peut avoir ouvert une transaction automatiquement.
        # Pour éviter "A transaction is already begun", on repart propre.
        if self.session.in_transaction():
            self.session.rollback()

        with self.session.begin():

            # 1) Verrou sur les lignes sélectionnées
            stmt = (
                select(LigneContrat)
                .where(LigneContrat.lc_id.in_(lc_ids))
                .with_for_update()
            )
            lignes = self.session.execute(stmt).scalars().all()

            # 2) Vérifier que toutes les lignes existent
            if len(lignes) != len(set(lc_ids)):
                raise ValueError("Une ou plusieurs lignes sont introuvables.")

            # 3) Vérifier qu'elles ne sont pas déjà restituées
            deja = [lc.lc_id for lc in lignes if lc.lc_dateretourreelle is not None]
            if deja:
                raise ValueError(f"Ligne(s) déjà restituée(s) : {deja}")

            # 4) Verrouiller les matériels correspondants
            mat_ids = [lc.mat_id for lc in lignes]
            mats = self.get_materiels_by_ids_for_update(mat_ids)

            # 5) Mise à jour des lignes : retour réel + retard + pénalité
            for lc in lignes:
                lc.lc_dateretourreelle = date_retour_reelle

                retard = (date_retour_reelle - lc.lc_dateretourprevue).days
                if retard < 0:
                    retard = 0
                lc.lc_retard_jours = retard

                # Règle simple : 5 €/jour
                lc.lc_penalite = retard * 5.00

            # 6) Remettre les matériels à Disponible
            for m in mats:
                m.mat_statut = "Disponible"

            print(
                "DEBUG: lignes modifiées:",
                [(lc.lc_id, lc.lc_dateretourreelle, lc.lc_retard_jours, lc.lc_penalite) for lc in lignes]
            )

            return lignes


    
