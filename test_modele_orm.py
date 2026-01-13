# Import de la fabrique de sessions SQLAlchemy.
# SessionLocal permet d'ouvrir une session de travail avec la base de données.
from dal.database import SessionLocal

# Import du modèle ORM Modele.
# Cette classe représente la table MODELE dans la base de données.
from dal.models import Modele


def main():
    """
    Fonction de test permettant de vérifier que :
    - la connexion à la base de données fonctionne via SQLAlchemy,
    - le modèle ORM Modele est correctement mappé,
    - les données de la table MODELE peuvent être lues.
    """

    # Ouverture d'une session SQLAlchemy.
    # Le bloc 'with' garantit que la session sera automatiquement fermée
    # à la fin de son utilisation, même en cas d'erreur.
    with SessionLocal() as db:

        # Requête ORM :
        # db.query(Modele) signifie :
        #   "sélectionner toutes les lignes de la table MODELE"
        # .all() retourne une liste d'objets Python de type Modele.
        modeles = db.query(Modele).all()

        # Parcours des modèles récupérés
        for m in modeles:
            # Chaque 'm' est un objet Python Modele.
            # Les attributs :
            # - m.mod_id       : identifiant unique du modèle
            # - m.mod_libelle  : libellé du modèle
            # - m.cat_id       : identifiant de la catégorie associée
            # - m.mar_id       : identifiant de la marque associée
            # correspondent aux colonnes de la table MODELE.
            print(m.mod_id, m.mod_libelle, m.cat_id, m.mar_id)


# Point d'entrée du script
# Ce code s'exécute uniquement si le fichier est lancé directement
# (et non s'il est importé depuis un autre module).
if __name__ == "__main__":
    main()
