# Import du type date pour créer de vraies dates Python
# (obligatoire pour SQLAlchemy avec SQLite)
from datetime import date

# Import des modèles ORM nécessaires au test
from dal.models import Categorie, Marque, Modele, Materiel

# Import du Repository à tester
from dal.repository import LocaMatRepository


def test_compteur_materiels_disponibles(db_session):
    """
    TEST : compteur des matériels disponibles

    Objectif :
    Vérifier que la méthode `get_materiels_disponibles()`
    du repository retourne UNIQUEMENT les matériels
    dont le statut est 'Disponible'.

    Le test suit la structure classique :
    - ARRANGE : préparation des données
    - ACT     : appel de la méthode testée
    - ASSERT  : vérification du résultat
    """

    # =========================
    # ARRANGE : préparation
    # =========================

    # Création d'une catégorie et d'une marque de test
    # Ces objets sont pour l'instant uniquement en mémoire
    cat = Categorie(cat_libelle="TestCat")
    mar = Marque(mar_libelle="TestMarque")

    # Ajout des objets à la session de test
    db_session.add_all([cat, mar])

    # Commit pour les insérer réellement en base
    # Cela permet d'obtenir cat.cat_id et mar.mar_id
    db_session.commit()

    # Création d'un modèle lié à la catégorie et à la marque
    mod = Modele(
        mod_libelle="TestModele",
        cat_id=cat.cat_id,
        mar_id=mar.mar_id
    )

    # Insertion du modèle en base
    db_session.add(mod)
    db_session.commit()

    # Création d'une date d'achat valide (objet date Python)
    d = date(2026, 1, 1)

    # Création d'un matériel DISPONIBLE (doit être retourné)
    m1 = Materiel(
        mat_serial="SN-TEST-001",
        mat_dateachat=d,
        mat_statut="Disponible",
        mod_id=mod.mod_id
    )

    # Création d'un matériel LOUÉ (ne doit PAS être retourné)
    m2 = Materiel(
        mat_serial="SN-TEST-002",
        mat_dateachat=d,
        mat_statut="Loué",
        mod_id=mod.mod_id
    )

    # Ajout des matériels à la session
    db_session.add_all([m1, m2])

    # Commit pour insérer les matériels en base
    db_session.commit()

    # =========================
    # ACT : action testée
    # =========================

    # Création du repository en lui injectant la session de test
    repo = LocaMatRepository(db_session)

    # Appel de la méthode à tester
    dispo = repo.get_materiels_disponibles()

    # =========================
    # ASSERT : vérifications
    # =========================

    # On vérifie qu'un seul matériel est retourné
    assert len(dispo) == 1

    # On vérifie que c'est bien le matériel disponible
    assert dispo[0].mat_serial == "SN-TEST-001"
