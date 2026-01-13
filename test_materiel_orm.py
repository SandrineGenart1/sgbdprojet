# Import de la fabrique de sessions SQLAlchemy.
# SessionLocal permet d'ouvrir une session de travail avec la base de données.
from dal.database import SessionLocal

# Import du modèle ORM Materiel.
# Cette classe représente la table MATERIEL dans la base de données.
from dal.models import Materiel


def main():
    """
    Fonction de test permettant de vérifier que :
    - la connexion à la base de données fonctionne via SQLAlchemy,
    - le modèle ORM Materiel est correctement mappé,
    - les données de la table MATERIEL peuvent être lues.
    """

    # Ouverture d'une session SQLAlchemy.
    # Le bloc 'with' garantit que la session sera automatiquement fermée
    # à la fin de son utilisation, même en cas d'erreur.
    with SessionLocal() as db:

        # Requête ORM :
        # db.query(Materiel) signifie :
        #   "sélectionner toutes les lignes de la table MATERIEL"
        # .all() retourne une liste d'objets Python de type Materiel.
        materiels = db.query(Materiel).all()

        # Parcours des matériels récupérés
        for mat in materiels:
            # Chaque 'mat' est un objet Python Materiel.
            # Les attributs :
            # - mat.mat_id      : identifiant unique du matériel
            # - mat.mat_serial  : numéro de série du matériel
            # - mat.mat_statut  : statut du matériel (Disponible, Loué, etc.)
            # - mat.mod_id      : identifiant du modèle associé
            # correspondent aux colonnes de la table MATERIEL.
            print(mat.mat_id, mat.mat_serial, mat.mat_statut, mat.mod_id)


# Point d'entrée du script
# Ce code s'exécute uniquement si le fichier est lancé directement
# (et non s'il est importé depuis un autre module).
if __name__ == "__main__":
    main()
