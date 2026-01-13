# Import de la fabrique de sessions SQLAlchemy.
# SessionLocal permet d'ouvrir une session de travail avec la base de données.
from dal.database import SessionLocal

# Import du modèle ORM Marque.
# Cette classe représente la table MARQUE dans la base de données.
from dal.models import Marque


def main():
    """
    Fonction de test permettant de vérifier que :
    - la connexion SQLAlchemy fonctionne,
    - le modèle ORM Marque est correctement défini,
    - les données de la table MARQUE peuvent être lues.
    """

    # Ouverture d'une session SQLAlchemy.
    # Le mot-clé 'with' garantit que la session sera correctement fermée
    # à la fin du bloc, même en cas d'erreur.
    with SessionLocal() as db:

        # Requête ORM :
        # db.query(Marque) signifie :
        #   "sélectionner toutes les lignes de la table MARQUE"
        # .all() retourne une liste d'objets Python de type Marque.
        marques = db.query(Marque).all()

        # Parcours des marques récupérées
        for m in marques:
            # Chaque 'm' est un objet Marque
            # Les attributs mar_id et mar_libelle correspondent
            # aux colonnes de la table MARQUE.
            print(m.mar_id, m.mar_libelle)


# Point d'entrée du script
# Ce code ne sera exécuté que si le fichier est lancé directement
# (et non s'il est importé dans un autre module).
if __name__ == "__main__":
    main()
