# bll/client_service.py
from dal.models import Client  # On utilise le modèle ORM comme structure de données (pas de requêtes ici)

# =========================
# Exception métier CLIENT
# =========================
class ClientError(Exception):
    """
    Exception métier liée aux clients.

    Cette exception est levée par la couche BLL lorsque
    une règle métier n'est pas respectée (champ manquant,
    donnée invalide, etc.).

    Elle permet de distinguer :
    - les erreurs métier (BLL)
    - des erreurs techniques (DAL / base de données)
    """
    pass


# =========================
# Service métier CLIENT
# =========================
class ClientService:
    """
    Service métier chargé de la gestion des clients.

    Rôle de cette classe :
    - appliquer les règles métier liées aux clients
    - valider les données reçues depuis l'interface (UI)
    - déléguer l'accès aux données à la DAL (repository)

    IMPORTANT :
    - cette classe ne contient AUCUNE requête SQL
    - elle ne connaît pas SQLAlchemy
    - elle reçoit un repository via injection de dépendance
    """

    def __init__(self, repo):
        """
        Constructeur du service.

        Injection de dépendance :
        - repo : instance de la couche DAL (ex: LocaMatRepository)

        Cela permet :
        - de séparer clairement la logique métier de l'accès aux données
        - de faciliter les tests et l'évolution du code
        """
        self.repo = repo

    def creer_client(
        self,
        prenom: str,
        nom: str,
        adresse: str,
        cp: str,
        tel: str,
        mail: str,
        vip: bool = False
    ):
        """
        Crée un nouveau client.

        Rôle de cette méthode :
        - valider les données du client selon les règles métier
        - préparer les données (nettoyage)
        - déléguer l'insertion en base de données à la DAL

        Règles métier appliquées :
        - tous les champs NOT NULL de la table CLIENT doivent être fournis
        - aucune logique SQL n'est autorisée dans cette méthode
        """

        # -------------------------
        # Nettoyage des données
        # -------------------------
        # Suppression des espaces inutiles et normalisation de l'email
        prenom = (prenom or "").strip()
        nom = (nom or "").strip()
        adresse = (adresse or "").strip()
        cp = (cp or "").strip()
        tel = (tel or "").strip()
        mail = (mail or "").strip().lower()

        # -------------------------
        # Vérifications métier alignées sur la table CLIENT
        # -------------------------
        # Si une règle n'est pas respectée, on lève une exception métier
        if not prenom:
            raise ClientError("Le prénom est obligatoire.")
        if not nom:
            raise ClientError("Le nom est obligatoire.")
        if not adresse:
            raise ClientError("L'adresse est obligatoire.")
        if not cp:
            raise ClientError("Le code postal est obligatoire.")
        if not tel:
            raise ClientError("Le téléphone est obligatoire.")
        if not mail:
            raise ClientError("L'email est obligatoire.")
        
        if "@" not in mail:
            raise ClientError("L'email doit contenir un @.")


        # -------------------------
        # Délégation à la DAL
        # -------------------------
        # Construction de l'objet Client (sans requête SQL)
        client = Client(
            cli_prenom=prenom,
            cli_nom=nom,
            cli_adresse=adresse,
            cli_cp=cp,
            cli_tel=tel,
            cli_mail=mail,
            cli_vip=vip
        )

        # Insertion via la DAL (commit / rollback gérés là-bas)
        return self.repo.add_client(client)
    
    def lister_clients(self):
        """Renvoie tous les clients (utilisé par l'UI)."""
        return self.repo.get_all_clients()
