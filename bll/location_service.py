# bll/location_service.py
"""
Couche BLL (Business Logic Layer) - Service "Location"

Ce fichier contient la logique métier de l'application (les règles).
Il NE CONTIENT PAS de requêtes SQL directes.

Architecture :
UI (Flask) → BLL (LocationService) → DAL (LocaMatRepository) → DB

Rôle du service :
- Valider les paramètres métier (dates, durée, etc.)
- Calculer le prix (remises / surcharge)
- Exposer des méthodes "simples" à l'UI
- Déléguer l'accès DB (transaction, verrous, insertions) au repository (DAL)
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


# =========================
# Exceptions métier
# =========================
class LocationError(Exception):
    """
    Exception métier : utilisée quand la demande utilisateur est invalide
    ou quand une règle applicative n'est pas respectée.
    """
    pass


# =========================
# DTO / objet de transfert
# =========================
@dataclass
class PrixDetail:
    """
    Objet simple (Data Transfer Object) renvoyé à l'UI.

    Il contient :
    - le total de base (avant remises)
    - les taux appliqués
    - le total final calculé
    """
    total_base: float
    remise_duree: float
    remise_vip: float
    surcharge_risque: float
    total_final: float


# =========================
# Service métier
# =========================
class LocationService:
    """
    Service métier pour :
    - valider une location (création contrat + lignes via DAL)
    - lister et traiter les restitutions
    - calculer prix / retard / pénalité
    - préparer l'affichage des contrats (statuts, pénalités totales)

    Important :
    - Le service reçoit un repository (DAL) via injection de dépendance.
    - Le service ne touche pas directement à SQLAlchemy ni aux requêtes.
    """

    # Règle simple de pénalité : 5€ par jour de retard
    PENALITE_PAR_JOUR = Decimal("5.00")

    def __init__(self, repo):
        """
        Constructeur du service.

        Injection de dépendance :
        - repo = instance de la DAL (LocaMatRepository)
        - permet de "brancher" la DB sans que la BLL connaisse SQLAlchemy

        Exemple :
        repo = LocaMatRepository(session)
        service = LocationService(repo)
        """
        self.repo = repo

    # ======================================================
    # 0) Méthodes simples exposées à l'UI
    # ======================================================

    def lister_clients(self):
        """
        Renvoie la liste des clients.
        L'UI (app.py) appelle cette méthode au lieu d'accéder à repo directement.
        """
        return self.repo.get_all_clients()

    def lister_contrats(self):
        """
        Renvoie tous les contrats (avec client + lignes + matériel)
        pour affichage dans l'interface.
        """
        return self.repo.get_all_contrats()

    # ======================================================
    # 1) CONTRATS : statut + résumé pour l'interface
    # ======================================================

    def determiner_statut_contrat(self, contrat) -> str:
        """
        Retourne un statut simple pour l'affichage :

        - "RETARD"  : au moins une ligne non restituée ET date prévue dépassée
        - "EN_COURS": au moins une ligne non restituée (mais pas en retard)
        - "TERMINE" : toutes les lignes sont restituées
        """
        aujourd_hui = date.today()

        # 1) Lignes non restituées (retour réel = NULL)
        non_restituees = [lc for lc in contrat.lignes if lc.lc_dateretourreelle is None]

        # 2) Si aucune ligne en attente -> contrat terminé
        if not non_restituees:
            return "TERMINE"

        # 3) Si au moins une ligne non restituée dépasse la date prévue -> retard en cours
        if any(lc.lc_dateretourprevue < aujourd_hui for lc in non_restituees):
            return "RETARD"

        # 4) Sinon -> contrat en cours sans retard
        return "EN_COURS"

    def lister_contrats_pour_ui(self):
        """
        Prépare une liste de contrats 'prêts pour l'UI'.

        On ajoute des infos utiles pour l'affichage :
        - statut : EN_COURS / RETARD / TERMINE
        - nb_non_restituees : nombre de lignes dont la date réelle est NULL
        - total_penalites : somme des pénalités déjà calculées (NULL => 0)
        """
        contrats = self.repo.get_all_contrats()
        resultats = []

        for c in contrats:
            # 1) Statut (calcul métier)
            statut = self.determiner_statut_contrat(c)

            # 2) Nombre de lignes non restituées
            nb_non_restituees = sum(1 for lc in c.lignes if lc.lc_dateretourreelle is None)

            # 3) Total des pénalités (Decimal)
            total_penalites = Decimal("0.00")
            for lc in c.lignes:
                if lc.lc_penalite is not None:
                    total_penalites += lc.lc_penalite

            resultats.append({
                "contrat": c,
                "statut": statut,
                "nb_non_restituees": nb_non_restituees,
                "total_penalites": total_penalites,
            })

        return resultats

    # ======================================================
    # 2) PRIX / VALIDATION LOCATION
    # ======================================================

    def calculer_prix(
        self,
        total_base: float,
        nb_jours: int,
        client_vip: bool,
        client_risque: bool
    ) -> PrixDetail:
        """
        Calcule un prix final à partir d'un total de base.

        Règles (exemple) :
        - Remise durée : -10% si plus de 7 jours
        - Remise VIP : -15% si client VIP
        - Surcharge risque : +5% si client a déjà rendu en retard

        Remarque :
        - On renvoie un PrixDetail pour que l'UI puisse afficher le détail.
        """

        # 1) Déterminer les taux à appliquer
        remise_duree = 0.10 if nb_jours > 7 else 0.0
        remise_vip = 0.15 if client_vip else 0.0
        surcharge_risque = 0.05 if client_risque else 0.0

        # 2) Appliquer les règles dans l'ordre
        total = total_base
        total = total * (1 - remise_duree)      # remises -> on réduit
        total = total * (1 - remise_vip)
        total = total * (1 + surcharge_risque)  # surcharge -> on augmente

        # 3) Retourner un objet "détail"
        return PrixDetail(
            total_base=total_base,
            remise_duree=remise_duree,
            remise_vip=remise_vip,
            surcharge_risque=surcharge_risque,
            total_final=round(total, 2)
        )

    def valider_location(
        self,
        client_id: int,
        materiel_ids: list[int],
        date_debut: date,
        date_fin: date
    ):
        """
        Valide une location (côté métier) puis délègue à la DAL la transaction.

        Ce que fait la BLL :
        - vérifie les dates
        - calcule la durée (nb_jours)

        Ce que fera la DAL (repo.transaction_valider_location) :
        - transaction atomique (BEGIN/COMMIT)
        - vérifie client
        - verrouille matériels (FOR UPDATE)
        - vérifie disponibilité
        - crée Contrat + Lignes
        - met statuts à 'Loué'
        - retourne contrat + matériels + prix_detail
        """

        # 1) Vérification métier des dates
        if date_fin < date_debut:
            raise LocationError("Dates invalides : la date de fin est avant la date de début.")

        # 2) Calcul du nombre de jours (inclusif)
        nb_jours = (date_fin - date_debut).days + 1
        if nb_jours <= 0:
            raise LocationError("La durée doit être d'au moins 1 jour.")

        # 3) On appelle la DAL
        #    On fournit aussi un "callback" pricing_callback :
        #    -> la DAL calculera total_base puis appellera self.calculer_prix(...)
        return self.repo.transaction_valider_location(
            client_id=client_id,
            materiel_ids=materiel_ids,
            date_debut=date_debut,
            date_fin=date_fin,
            nb_jours=nb_jours,
            pricing_callback=self.calculer_prix
        )

    # ======================================================
    # 3) RETARD / PENALITES (utilitaires)
    # ======================================================

    def calculer_retard_jours(self, date_prevue: date, date_reelle: date) -> int:
        """
        Calcule le retard en jours.

        - Si rendu à l'heure ou en avance => 0
        - Sinon => différence en jours
        """
        if date_reelle <= date_prevue:
            return 0
        return (date_reelle - date_prevue).days

    def calculer_penalite(self, retard_jours: int) -> Decimal:
        """
        Calcule la pénalité à partir du retard en jours.

        Exemple :
        - 3 jours de retard -> 3 * 5.00 = 15.00
        """
        return (self.PENALITE_PAR_JOUR * Decimal(retard_jours)).quantize(Decimal("0.01"))

    def calculer_retard_et_penalite(self, date_prevue: date, date_reelle: date) -> tuple[int, Decimal]:
        """
        Méthode utilitaire :
        renvoie (retard, penalite) en une seule fois.
        """
        retard = self.calculer_retard_jours(date_prevue, date_reelle)
        penalite = self.calculer_penalite(retard)
        return retard, penalite

    # ======================================================
    # 4) RESTITUTIONS
    # ======================================================

    def lister_lignes_a_restituer(self):
        """
        Renvoie les lignes de contrat non restituées (retour réel = NULL).

        La DAL fait déjà le bon eager-loading pour éviter DetachedInstanceError.
        """
        return self.repo.get_lignes_a_restituer()

    def restituer(self, lc_ids: list[int], date_retour_reelle: date):
        """
        Restitue une ou plusieurs lignes.

        Côté BLL :
        - validation métier simple (date obligatoire)

        Côté DAL :
        - transaction atomique
        - verrou des lignes et matériels
        - mise à jour retour réel, retard, pénalité
        - remise du statut matériel à 'Disponible'
        """
        if date_retour_reelle is None:
            raise LocationError("Veuillez choisir une date de retour réelle.")

        return self.repo.transaction_restituer_lignes(lc_ids, date_retour_reelle)
