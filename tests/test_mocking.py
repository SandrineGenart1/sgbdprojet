from unittest.mock import MagicMock

from dal.models import Materiel
from dal.repository import LocaMatRepository


def test_louer_materiel_succes_mock():
    """
    Test unitaire avec mocking (sans base de données).

    Idée :
    - on remplace la Session SQLAlchemy par un MagicMock
    - on "force" session.get(...) à renvoyer un objet Materiel
    - on vérifie que :
        - la méthode renvoie True
        - le statut passe à 'Loué'
        - commit() est bien appelé
    """

    # ARRANGE : fausse session SQLAlchemy
    mock_session = MagicMock()

    # Faux matériel (comme si la DB l'avait renvoyé)
    faux_mat = Materiel(mat_id=1, mat_serial="SN-MOCK-001", mat_statut="Disponible", mod_id=1)

    # Quand le repository fera session.get(Materiel, 1) => il recevra faux_mat
    mock_session.get.return_value = faux_mat

    repo = LocaMatRepository(mock_session)

    # ACT
    resultat = repo.louer_materiel(1)

    # ASSERT
    assert resultat is True
    assert faux_mat.mat_statut == "Loué"
    mock_session.commit.assert_called_once()


def test_louer_materiel_introuvable_mock():
    """
    Cas d'erreur :
    - session.get(...) renvoie None (matériel absent)
    - la méthode doit renvoyer False et ne pas commit
    """
    mock_session = MagicMock()
    mock_session.get.return_value = None

    repo = LocaMatRepository(mock_session)

    resultat = repo.louer_materiel(999)

    assert resultat is False
    mock_session.commit.assert_not_called()


def test_louer_materiel_deja_loue_mock():
    """
    Cas d'erreur :
    - le matériel existe mais n'est pas 'Disponible'
    - la méthode renvoie False et ne commit pas
    """
    mock_session = MagicMock()
    faux_mat = Materiel(mat_id=2, mat_serial="SN-MOCK-002", mat_statut="Loué", mod_id=1)
    mock_session.get.return_value = faux_mat

    repo = LocaMatRepository(mock_session)

    resultat = repo.louer_materiel(2)

    assert resultat is False
    mock_session.commit.assert_not_called()
