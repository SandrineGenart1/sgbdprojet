# On importe la fabrique de sessions SQLAlchemy.
# SessionLocal permet de créer une session de travail avec la base de données.
from dal.database import SessionLocal

# On importe le modèle ORM Categorie.
# Cette classe représente la table CATEGORIE de la base de données.
from dal.models import Categorie


def main():
    """
    Fonction de test permettant de vérifier que :
    - la connexion à la base de données fonctionne,
    - le modèle ORM Categorie est correctement mappé,
    - les données existantes peuvent être lues via SQLAlchemy.
    """

    # Ouverture d'une session SQLAlchemy.
    # Le mot-clé 'with' garantit que la session sera fermée automatiquement
    # à la fin du bloc, même en cas d'erreur.
    with SessionLocal() as db:

        # Requête ORM :
        # db.query(Categorie) signifie :
        #   "sélectionner toutes les lignes de la table CATEGORIE"
        # .all() retourne le résultat sous forme d'une liste d'objets Categorie.
        categories = db.query(Categorie).all()

        # Parcours des catégories récupérées
        for c in categories:
            # Chaque 'c' est un objet Python de type Categorie
            # Ses attributs correspondent aux colonnes de la table
            print(c.cat_id, c.cat_libelle)


# Point d'entrée du script
# Ce test ne sera exécuté que si le fichier est lancé directement
# et pas s'il est importé comme module.
if __name__ == "__main__":
    main()
