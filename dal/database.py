"""
Module database.py
==================

Ce module est responsable de la configuration de l'accès à la base de données
via SQLAlchemy.

Rôle de ce module :
- Lire les paramètres de connexion depuis le fichier .env (en local)
- Construire l'URL de connexion à la base de données
- Créer le moteur SQLAlchemy (engine)
- Fournir une fabrique de sessions (SessionLocal)
- Définir la classe de base pour tous les modèles ORM

IMPORTANT (industrialisation / CI) :
- En environnement CI (GitHub Actions), le fichier .env n'existe PAS
- Les tests pytest importent Base depuis ce module
- Donc ce module ne doit PAS lever d'erreur à l'import
- En CI, on bascule automatiquement vers SQLite en mémoire
"""

import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# ---------------------------------------------------------------------------
# Chargement des variables d'environnement
# ---------------------------------------------------------------------------
# En local :
#   - le fichier .env existe et contient les infos PostgreSQL
# En CI (GitHub Actions) :
#   - le fichier .env n'existe pas (il est ignoré par .gitignore)
#   - load_dotenv() ne plante pas, il ne charge simplement rien
load_dotenv()


# ---------------------------------------------------------------------------
# Classe de base pour les modèles ORM
# ---------------------------------------------------------------------------
# Toutes les classes ORM (Client, Materiel, Contrat, etc.)
# hériteront de cette classe Base.
class Base(DeclarativeBase):
    """
    Classe de base SQLAlchemy pour tous les modèles ORM.

    Chaque classe représentant une table héritera de cette classe.
    """
    pass


# ---------------------------------------------------------------------------
# Construction de l'URL de connexion
# ---------------------------------------------------------------------------
def build_database_url() -> str:
    """
    Construit l'URL de connexion SQLAlchemy.

    Fonctionnement :
    - En local : utilise PostgreSQL via les variables du fichier .env
    - En tests / CI : bascule automatiquement vers SQLite en mémoire

    Variables attendues dans le fichier .env (local uniquement) :
    - DB_HOST
    - DB_NAME
    - DB_USER
    - DB_PASSWORD
    - DB_PORT (optionnel, 5432 par défaut)

    Returns:
        str : URL de connexion compatible avec SQLAlchemy
    """

    host = os.getenv("DB_HOST")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    port = os.getenv("DB_PORT", "5432")

    # -----------------------------------------------------------------------
    # CAS 1 — Variables PostgreSQL absentes
    # -----------------------------------------------------------------------
    # Cela arrive dans deux situations normales :
    # - tests pytest
    # - GitHub Actions (CI)
    #
    # Dans ce cas :
    # - on NE veut PAS lever d'erreur
    # - on utilise SQLite en mémoire pour permettre aux tests de s'exécuter
    if not all([host, name, user, password]):
        if (
            os.getenv("PYTEST_CURRENT_TEST")   # pytest
            or os.getenv("GITHUB_ACTIONS")     # GitHub Actions
            or os.getenv("CI")                 # autre CI
        ):
            return "sqlite+pysqlite:///:memory:"

        # -------------------------------------------------------------------
        # CAS 2 — Exécution locale sans .env
        # -------------------------------------------------------------------
        # Ici, c'est une vraie erreur de configuration
        raise ValueError(
            "Variables d'environnement manquantes. "
            "Vérifie DB_HOST, DB_NAME, DB_USER et DB_PASSWORD dans le fichier .env."
        )

    # -----------------------------------------------------------------------
    # CAS 3 — Exécution locale normale avec PostgreSQL
    # -----------------------------------------------------------------------
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"


# ---------------------------------------------------------------------------
# Création du moteur SQLAlchemy
# ---------------------------------------------------------------------------
# L'engine représente la connexion centrale à la base de données.
# SQLAlchemy l'utilise pour exécuter toutes les requêtes.
DATABASE_URL = build_database_url()

engine = create_engine(
    DATABASE_URL,
    echo=False  # Mettre True pour afficher les requêtes SQL (debug)
)


# ---------------------------------------------------------------------------
# Fabrique de sessions
# ---------------------------------------------------------------------------
# Une session représente une "conversation" avec la base de données.
# Elle est utilisée par :
# - la DAL (repository)
# - la BLL
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
