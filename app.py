"""
app.py
======

C'est le point d’entrée de l’interface web Flask (UI).

Rôle de ce fichier :
- Définir les routes HTTP (URLs)
- Appeler la couche BLL (CatalogueService)
- Transmettre les données aux templates HTML (avec Jinja2)

Règles IMPORTANTES respectées :
- AUCUNE requête SQL ici
- AUCUN accès ORM direct
- La logique métier est dans la BLL
- L’accès aux données est dans la DAL
"""

import os

# Flask = framework web
from flask import Flask, render_template
from flask import request, redirect, url_for, flash

# Import de la BLL
from bll.catalogue_service import CatalogueService
from bll.dashboard_service import DashboardService

# Import DAL : session + repository
from dal.database import SessionLocal
from dal.repository import LocaMatRepository


from datetime import date
from bll.location_service import LocationService, LocationError



# -----------------------------------------------------------------------------
# Création de l'application Flask
# -----------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

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

def build_location_service(session):
    repo = LocaMatRepository(session)
    return LocationService(repo)

def build_dashboard_service(session):
    repo = LocaMatRepository(session)
    return DashboardService(repo)



# =========================
# ROUTE : PAGE D’ACCUEIL
# =========================
@app.get("/")
def home():
    """
    GET /
    Affiche la page d'accueil (tableau de bord).
    """
    with SessionLocal() as session:
        dashboard = build_dashboard_service(session)
        data = dashboard.get_dashboard()

    return render_template("home.html", data=data)


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

# ==================================
# ROUTE GET: Fromulaire de location
# =================================
@app.get("/locations/nouveau")
def location_nouveau():
    with SessionLocal() as session:
        catalogue = build_catalogue_service(session)
        location_service = build_location_service(session)

        clients =  location_service.lister_clients()
        materiels = catalogue.lister_materiels_disponibles()

    return render_template("location_nouveau.html", clients=clients, materiels=materiels)

# =========================
# ROUTE POST: valider location
# =========================
@app.post("/locations/valider")
def location_valider():
    try:
        client_id = int(request.form["client_id"])
        materiel_ids = [int(x) for x in request.form.getlist("materiel_ids")]

        date_debut = date.fromisoformat(request.form["date_debut"])
        date_fin = date.fromisoformat(request.form["date_fin"])

        with SessionLocal() as session:
            location_service = build_location_service(session)

            contrat, materiels, prix_detail = location_service.valider_location(
                client_id=client_id,
                materiel_ids=materiel_ids,
                date_debut=date_debut,
                date_fin=date_fin
            )

        return render_template(
            "location_ok.html",
            contrat=contrat,
            materiels=materiels,
            prix=prix_detail
        )

    except (ValueError, LocationError) as e:
        flash(str(e))
        return redirect(url_for("location_nouveau"))
    

@app.get("/contrats")
def contrats():
    with SessionLocal() as session:
        location_service = build_location_service(session)
        contrats_ui = location_service.lister_contrats_pour_ui()

    return render_template("contrats.html", contrats_ui=contrats_ui)
    

# ======================================================
# ROUTES : RESTITUTIONS 
# ======================================================

@app.get("/restitutions")
def restitutions():
    with SessionLocal() as session:
        location_service = build_location_service(session)
        lignes = location_service.lister_lignes_a_restituer()

    return render_template("restitutions.html", lignes=lignes)


@app.post("/restitutions/valider")
def restitutions_valider():
    try:
        lc_ids = [int(x) for x in request.form.getlist("lc_ids")]

        date_retour_str = request.form.get("date_retour_reelle", "").strip()
        if not date_retour_str:
            raise LocationError("Veuillez choisir une date de retour réelle.")
        date_retour_reelle = date.fromisoformat(date_retour_str)

        with SessionLocal() as session:
            location_service = build_location_service(session)
            location_service.restituer(lc_ids, date_retour_reelle)

        flash("Restitution enregistrée.")
        return redirect(url_for("restitutions"))

    except (ValueError, LocationError) as e:
        flash(str(e))
        return redirect(url_for("restitutions"))




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
