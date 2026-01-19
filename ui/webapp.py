"""
Mini application Flask (UI Web).

Règle d'architecture :
UI (Flask) -> BLL -> DAL -> DB
Aucune requête SQLAlchemy directe ici.
"""

from flask import Flask, render_template

from bll.catalogue_service import CatalogueService

app = Flask(__name__)
service = CatalogueService()


@app.get("/")
def index():
    # On appelle la BLL
    materiels = service.lister_materiels_disponibles()
    return render_template("index.html", materiels=materiels)


if __name__ == "__main__":
    # En local
    app.run(debug=True)
