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

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
" on ajoute foreignkey car on l'utilise dans model"
from dal.database import Base


class Client(Base):
    """
    On crée une classe Python => Elle hérite de Base, ce qui dit à SQLAlchemy : 
    “Cette classe représente une table de la base de données”
    C'est un Modèle ORM correspondant à la table CLIENT.

    Cette classe permet à SQLAlchemy de manipuler les clients via des objets Python
    au lieu d'écrire des requêtes SQL directement.

    Table : CLIENT
    Clé primaire : cli_id
    Contrainte : cli_mail est unique

    Clé primaire / clés étrangères : Ces contraintes doivent être écrites dans le modèle ORM.
    NOT NULL → aussi : À écrire avec : nullable=False

    UNIQUE → OUI (mais sans excès Exemples : unique=True
    Permet de refléter la contrainte métier, SQLAlchemy peut lever une IntegrityError 
    Cohérence entre DB et ORM

    CHECK → ⚠️ NON dans l’ORM Exemple SQL :
    CHECK (mat_statut IN ('Disponible', 'Loué', 'En maintenance', 'Rebut'))
    Pourquoi ?SQLAlchemy ne gère pas bien les CHECK complexes en lecture seule
    La contrainte existe déjà dans la base
    Elle doit rester au niveau SGBD
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


class Categorie(Base):
    """
    Modèle ORM correspondant à la table CATEGORIE.
    """

    __tablename__ = "categorie"

    cat_id = Column(Integer, primary_key=True)
    cat_libelle = Column(String(50), nullable=False, unique=True)


class Marque(Base):
    """
    Modèle ORM correspondant à la table MARQUE.

    Une marque représente le fabricant d’un matériel (ex : HP, Dell, Canon, etc.).

    Table : MARQUE
    Clé primaire : mar_id
    Contrainte : mar_libelle est unique
    """
    __tablename__ = "marque"

    mar_id = Column(Integer, primary_key=True)
    mar_libelle = Column(String(50), nullable=False, unique=True)



class Modele(Base):
    """
    Modèle ORM correspondant à la table MODELE.

    Un modèle représente un type précis de matériel,
    associé à une catégorie et à une marque.

    Table : MODELE
    Clé primaire : mod_id
    Clés étrangères :
      - cat_id → CATEGORIE
      - mar_id → MARQUE
    """

    __tablename__ = "modele"

    mod_id = Column(Integer, primary_key=True)
    mod_libelle = Column(String(50), nullable=False)

    # Clés étrangères
    cat_id = Column(Integer, ForeignKey("categorie.cat_id"), nullable=False)
    mar_id = Column(Integer, ForeignKey("marque.mar_id"), nullable=False)



