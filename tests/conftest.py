import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dal.database import Base  # ta Base declarative_base()
from dal.models import Client, Categorie, Marque, Modele, Materiel, Contrat, LigneContrat

# Base de test en mémoire (ultra rapide, détruite à la fin)
TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """
    Moteur SQLAlchemy partagé pour la session de tests.
    On utilise SQLite en mémoire pour éviter d'utiliser PostgreSQL en tests.
    """
    return create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})


@pytest.fixture(scope="function")
def db_session(engine):
    """
    Fixture centrale (Arrange automatique) :
    - Crée toutes les tables AVANT chaque test
    - Fournit une session SQLAlchemy au test
    - Supprime toutes les tables APRÈS le test

    But : chaque test est indépendant (Test B n'est jamais influencé par Test A).
    """
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()

    yield session  # le test s'exécute ici

    session.close()
    Base.metadata.drop_all(bind=engine)
