"""
Module models.py
================

Ce module contient les classes ORM (SQLAlchemy) qui représentent les tables
de la base de données.

Rôle :
- Une table SQL -> une classe Python
- Une colonne -> un attribut (Column)
- Les relations (Foreign Key) seront ajoutées plus tard, étape par étape.

IMPORTANT :
Aucune requête SQL n'est écrite ici.
Aucune logique métier n'est écrite ici.
"""

from sqlalchemy import Column, Integer, String, Boolean
from dal.database import Base


class Client(Base):
    """
    Modèle ORM correspondant à la table CLIENT.

    Cette classe permet à SQLAlchemy de manipuler les clients via des objets Python
    au lieu d'écrire des requêtes SQL directement.

    Table : CLIENT
    Clé primaire : cli_id
    Contrainte : cli_mail est unique
    """

    # Nom de la table dans PostgreSQL.
    # Comme quand on a créé CREATE TABLE CLIENT sans guillemets, PostgreSQL la stocke
    # généralement en minuscules : "client".
    __tablename__ = "client"

    # Colonnes de la table CLIENT
    cli_id = Column(Integer, primary_key=True)

    cli_prenom = Column(String(50), nullable=False)
    cli_nom = Column(String(50), nullable=False)

    cli_adresse = Column(String(50), nullable=False)
    cli_cp = Column(String(10), nullable=False)

    cli_tel = Column(String(20), nullable=False)
    cli_mail = Column(String(50), nullable=False, unique=True)

    cli_vip = Column(Boolean, nullable=True)
