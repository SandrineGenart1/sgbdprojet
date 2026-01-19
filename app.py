"""
app.py
======

Point d’entrée de l’interface web Flask (UI).

Rôle de ce fichier :
- Définir les routes HTTP (URLs)
- Appeler la couche BLL (CatalogueService)
- Transmettre les données aux templates HTML (Jinja2)

Règles IMPORTANTES respectées :
- ❌ AUCUNE requête SQL ici
- ❌ AUCUN accès ORM direct
- ✅ La logique métier est dans la BLL
- ✅ L’accès aux données est dans la DAL
"""

import os

# Flask = framework web
from flask import Flask, render_template

# Import de la BLL
from bll.catalogue_service import CatalogueService

# Import DAL : session + repository
from dal.database import SessionLocal
from dal.repository import LocaMatRepository


# -----------------------------------------------------------------------------
# Création de l'application Flask
# -----------------------------------------------------------------------------
app = Flask(__name__)


# -----------------------------------------------------------------------------
# Fonction utilitaire : fabriquer le service BLL proprement
# -----------------------------------------------------------------------------
def build_catalogue_service(session):
    """
    Construit un CatalogueService à partir d'une session SQLAlchemy.

    Pourquoi faire une fonction ?
    - Pour éviter de répéter 3 lignes dans chaque route :
        repo = LocaMatRepository(session)
        service = CatalogueService(repo)
        ...
    - Et garder app.py propre / lisible.
    """
    repo = LocaMatRepository(session)        # DAL (accès aux données)
    service = CatalogueService(repo)         # BLL (orchestration)
    return service


# =========================
# ROUTE : PAGE D’ACCUEIL
# =========================
@app.get("/")
def home():
    """
    GET /

    Affiche la page d'accueil.
    Aucune logique métier ici : on rend juste un template.
    """
    return render_template("home.html")


# =========================
# ROUTE : MATÉRIELS DISPONIBLES
# =========================
@app.get("/materiels/disponibles")
def materiels_disponibles():
    """
    GET /materiels/disponibles

    Affiche la liste des matériels disponibles.

    Étapes :
    1. Ouvrir une session SQLAlchemy (UI gère le cycle de vie)
    2. Construire le service BLL (qui utilise le repository DAL)
    3. Appeler la méthode BLL
    4. Envoyer le résultat au template Jinja2
    """
    with SessionLocal() as session:
        service = build_catalogue_service(session)
        materiels = service.lister_materiels_disponibles()

    return render_template("materiels.html", materiels=materiels)


# =========================
# ROUTE : CATÉGORIES
# =========================
@app.get("/categories")
def categories():
    """
    GET /categories

    Affiche la liste des catégories.
    """
    with SessionLocal() as session:
        service = build_catalogue_service(session)
        categories = service.lister_categories()

    return render_template("categories.html", categories=categories)


# =========================
# ROUTE : MARQUES
# =========================
@app.get("/marques")
def marques():
    """
    GET /marques

    Affiche la liste des marques.
    """
    with SessionLocal() as session:
        service = build_catalogue_service(session)
        marques = service.lister_marques()

    return render_template("marques.html", marques=marques)


# =========================
# LANCEMENT DE L’APP
# =========================
if __name__ == "__main__":
    """
    Ce bloc ne s'exécute que si on lance :
        py app.py

    Sur Render (ou en prod), on lance Flask autrement,
    donc ce bloc ne servira qu'en local.
    """

    # Debug = True uniquement en local.
    # Sur Render, on veut False.
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode)
