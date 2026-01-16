import pytest
from sqlalchemy.exc import IntegrityError

from dal.models import Client


def test_client_creation_valide(db_session):
    """Happy path : un client complet s'enregistre."""
    c = Client(
        cli_prenom="Sandrine",
        cli_nom="Genart",
        cli_adresse="Rue Test 1",
        cli_cp="7500",
        cli_tel="000",
        cli_mail="sandrine.genart@test.local",
        cli_vip=False,
    )
    db_session.add(c)
    db_session.commit()

    assert c.cli_id is not None
    assert c.cli_mail == "sandrine.genart@test.local"


def test_client_mail_unique(db_session):
    """UNIQUE : on ne peut pas créer deux clients avec le même email."""
    c1 = Client(
        cli_prenom="A",
        cli_nom="A",
        cli_adresse="X",
        cli_cp="1",
        cli_tel="1",
        cli_mail="unique@test.local",
        cli_vip=False,
    )
    c2 = Client(
        cli_prenom="B",
        cli_nom="B",
        cli_adresse="Y",
        cli_cp="2",
        cli_tel="2",
        cli_mail="unique@test.local",  # même email -> doit échouer
        cli_vip=False,
    )

    db_session.add(c1)
    db_session.commit()

    db_session.add(c2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_client_sans_nom(db_session):
    """NOT NULL : cli_nom obligatoire."""
    c = Client(
        cli_prenom="NoName",
        # cli_nom manquant
        cli_adresse="Rue Test",
        cli_cp="7500",
        cli_tel="000",
        cli_mail="noname@test.local",
        cli_vip=False,
    )
    db_session.add(c)
    with pytest.raises(IntegrityError):
        db_session.commit()
