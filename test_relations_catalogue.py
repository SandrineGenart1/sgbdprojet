# Import de la fabrique de sessions SQLAlchemy.
# SessionLocal permet d'ouvrir une session de travail avec la base de données.
from dal.database import SessionLocal

# Import du modèle ORM Materiel.
# Materiel est la table centrale ici, car elle permet de remonter vers :
# - le modèle
# - la marque
# - la catégorie
from dal.models import Materiel


def main():
    """
    Fonction de test permettant de vérifier que les relations ORM
    entre les tables du catalogue fonctionnent correctement.

    Objectif :
    - accéder à des données liées sans écrire de requêtes SQL
    - naviguer entre les objets grâce aux relationships SQLAlchemy
    """

    # Ouverture d'une session SQLAlchemy.
    # Le mot-clé 'with' garantit que la session sera automatiquement fermée
    # à la fin du bloc, même en cas d'erreur.
    with SessionLocal() as db:

        # Requête ORM :
        # db.query(Materiel) signifie :
        #   "sélectionner des lignes dans la table MATERIEL"
        # .limit(5) limite le résultat à 5 matériels
        # .all() retourne une liste d'objets Materiel
        materiels = db.query(Materiel).limit(5).all()

        # Parcours des matériels récupérés
        for mat in materiels:
            # Grâce aux relations ORM, on peut accéder directement :
            # - au modèle du matériel
            # - à la marque du modèle
            # - à la catégorie du modèle
            #
            # Sans relationship(), il aurait fallu écrire des jointures SQL.
            print(
                mat.mat_id,                   # identifiant du matériel
                mat.mat_serial,               # numéro de série
                mat.mat_statut,               # statut (Disponible, Loué, etc.)
                "->",
                mat.modele.mod_libelle,       # libellé du modèle
                "|",
                mat.modele.marque.mar_libelle,    # marque du modèle
                "|",
                mat.modele.categorie.cat_libelle  # catégorie du modèle
            )


# Point d'entrée du script
# Ce code ne s'exécute que si le fichier est lancé directement
# et non s'il est importé depuis un autre module.
#Cette condition permet d’exécuter le code uniquement lorsque le fichier 
# est lancé directement, et d’éviter son exécution automatique 
# lorsqu’il est importé comme module.
if __name__ == "__main__":
    main()
