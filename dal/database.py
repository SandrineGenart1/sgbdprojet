"""
Module database.py
==================

Ce module est responsable de la configuration de l'accès à la base de données
via SQLAlchemy.

Rôle de ce module :
- Lire les paramètres de connexion depuis le fichier .env
- Créer le moteur SQLAlchemy (engine)
- Fournir une fabrique de sessions (SessionLocal)
- Définir la classe de base pour tous les modèles ORM

IMPORTANT :
Ce module NE contient PAS de requêtes SQL.
Il sert uniquement d'infrastructure technique pour le DAL.
"""

import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# ---------------------------------------------------------------------------
# Chargement des variables d'environnement
# ---------------------------------------------------------------------------
# Le fichier .env contient les informations sensibles (login, mot de passe, etc.)
# Cela évite de les écrire en clair dans le code source.
load_dotenv()


def build_database_url() -> str:
    """
    Construit l'URL de connexion SQLAlchemy à partir des variables du fichier .env.

    Variables attendues dans le fichier .env :
    - DB_HOST : adresse du serveur PostgreSQL
    - DB_NAME : nom de la base de données
    - DB_USER : utilisateur PostgreSQL
    - DB_PASSWORD : mot de passe PostgreSQL
    - DB_PORT : port PostgreSQL (optionnel, 5432 par défaut)

    Returns:
        str : URL de connexion compatible avec SQLAlchemy et psycopg.
    """

    host = os.getenv("DB_HOST")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    port = os.getenv("DB_PORT", "5432")

    # Sécurité : on vérifie que les informations indispensables sont présentes
    if not all([host, name, user, password]):
        raise ValueError(
            "Variables d'environnement manquantes. "
            "Vérifie DB_HOST, DB_NAME, DB_USER et DB_PASSWORD dans le fichier .env."
        )

    # Format standard SQLAlchemy pour PostgreSQL avec psycopg (v3)
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"


# ---------------------------------------------------------------------------
# Création du moteur SQLAlchemy
# ---------------------------------------------------------------------------
# L'engine représente la connexion "centrale" à la base de données.
# SQLAlchemy s'en sert pour exécuter toutes les opérations.
DATABASE_URL = build_database_url()

engine = create_engine(
    DATABASE_URL,
    echo=False  # Mettre True pour afficher les requêtes SQL (utile pour debug)
)


# ---------------------------------------------------------------------------
# Fabrique de sessions
# ---------------------------------------------------------------------------
# Une session représente une "conversation" avec la base de données.
# Elle est utilisée dans le repository et la BLL.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# ---------------------------------------------------------------------------
# Classe de base pour les modèles ORM
# ---------------------------------------------------------------------------
# Toutes les classes représentant des tables hériteront de Base.
class Base(DeclarativeBase):
    """
    Classe de base SQLAlchemy pour tous les modèles ORM.

    Chaque classe représentant une table héritera de cette classe.
    """
    pass
