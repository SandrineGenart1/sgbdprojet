"""
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

IMPORTANT (Render / prod) :
- Sur Render, on fournit généralement une seule variable : DATABASE_URL
- Neon impose SSL => on met ?sslmode=require dans l'URL (côté variable)
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
# En CI / Render :
#   - le fichier .env peut ne pas exister
#   - load_dotenv() ne plante pas, il ne charge simplement rien
load_dotenv()


# ---------------------------------------------------------------------------
# Classe de base pour les modèles ORM
# ---------------------------------------------------------------------------
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

    Priorité (du plus courant en prod au plus courant en local) :
    1) DATABASE_URL (Render / prod)
    2) DB_HOST + DB_NAME + DB_USER + DB_PASSWORD (+ DB_PORT) (local)
    3) SQLite mémoire si contexte de tests/CI

    Returns:
        str : URL de connexion compatible avec SQLAlchemy
    """

    # -----------------------------------------------------------------------
    # CAS 0 — DATABASE_URL fourni (Render / prod)
    # -----------------------------------------------------------------------
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # IMPORTANT :
        # - Pour Neon, l'URL doit contenir sslmode=require
        # - Exemple : postgresql://user:pwd@host/db?sslmode=require
        #
        # Render fournit parfois "postgres://..." (ancien schéma) :
        # SQLAlchemy préfère "postgresql://..."
        if database_url.startswith("postgres://"):
            database_url = "postgresql://" + database_url[len("postgres://"):]
        return database_url

    # -----------------------------------------------------------------------
    # CAS 1 — Variables PostgreSQL "détaillées" (local)
    # -----------------------------------------------------------------------
    host = os.getenv("DB_HOST")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    port = os.getenv("DB_PORT", "5432")

    # -----------------------------------------------------------------------
    # CAS 2 — Variables PostgreSQL absentes (tests / CI)
    # -----------------------------------------------------------------------
    if not all([host, name, user, password]):
        if (
            os.getenv("PYTEST_CURRENT_TEST")   # pytest
            or os.getenv("GITHUB_ACTIONS")     # GitHub Actions
            or os.getenv("CI")                 # autre CI
        ):
            return "sqlite+pysqlite:///:memory:"

        # -------------------------------------------------------------------
        # CAS 3 — Exécution locale sans config
        # -------------------------------------------------------------------
        raise ValueError(
            "Variables d'environnement manquantes. "
            "Fournis DATABASE_URL (prod) ou DB_HOST/DB_NAME/DB_USER/DB_PASSWORD (local)."
        )

    # -----------------------------------------------------------------------
    # CAS 4 — Exécution locale normale avec PostgreSQL
    # -----------------------------------------------------------------------
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"


# ---------------------------------------------------------------------------
# Création du moteur SQLAlchemy
# ---------------------------------------------------------------------------
DATABASE_URL = build_database_url()

engine = create_engine(
    DATABASE_URL,
    echo=False,         # True si tu veux voir les requêtes SQL en debug
    pool_pre_ping=True  # évite des erreurs de connexions "stales" sur cloud
)


# ---------------------------------------------------------------------------
# Fabrique de sessions
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)
