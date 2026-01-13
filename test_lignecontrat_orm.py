# Import de la fabrique de sessions SQLAlchemy.
# SessionLocal permet d'ouvrir une session de travail avec la base de données.
from dal.database import SessionLocal

# Import du modèle ORM LigneContrat.
# Cette classe représente la table LIGNECONTRAT dans la base de données.
from dal.models import LigneContrat


def main():
    """
    Fonction de test permettant de vérifier que :
    - la connexion à la base de données fonctionne via SQLAlchemy,
    - le modèle ORM LigneContrat est correctement mappé,
    - les données de la table LIGNECONTRAT peuvent être lues.
    """

    # Ouverture d'une session SQLAlchemy.
    # Le bloc 'with' garantit que la session sera automatiquement fermée
    # automatiquement à la fin du bloc, même en cas d'erreur.
    with SessionLocal() as db:

        # Requête ORM :
        # db.query(LigneContrat) signifie :
        #   "sélectionner toutes les lignes de la table LIGNECONTRAT"
        # .all() retourne une liste d'objets Python de type LigneContrat.
        lignes = db.query(LigneContrat).all()

        # Parcours des lignes de contrat récupérées
        for lc in lignes:
            # Chaque 'lc' est un objet Python LigneContrat.
            # Les attributs :
            # - lc.lc_id                : identifiant unique de la ligne de contrat
            # - lc.cont_id              : identifiant du contrat associé
            # - lc.mat_id               : identifiant du matériel loué
            # - lc.lc_dateretourprevue  : date de retour prévue
            # - lc.lc_dateretourreelle  : date de retour réelle (None si pas encore rendu)
            # correspondent aux colonnes de la table LIGNECONTRAT.
            print(
                lc.lc_id,
                lc.cont_id,
                lc.mat_id,
                lc.lc_dateretourprevue,
                lc.lc_dateretourreelle
            )


# Point d'entrée du script
# Ce code ne s'exécute que si le fichier est lancé directement
# et non s'il est importé comme module dans un autre fichier.
if __name__ == "__main__":
    main()
