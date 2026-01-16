from dal.database import SessionLocal
from dal.repository import LocaMatRepository
from dal.models import Client


def main():
    with SessionLocal() as session:
        repo = LocaMatRepository(session)

        nouveau = Client(
            cli_prenom="Test2",
            cli_nom="Clien2t",
            cli_adresse="Rue de test 1",
            cli_cp="75000",
            cli_tel="000000000",
            cli_mail="test.client2@example.com",
            cli_vip=False,
        )

        insere = repo.add_client(nouveau)
        print("CLIENT INSERE:", insere.cli_id, insere.cli_nom, insere.cli_prenom, insere.cli_mail)


if __name__ == "__main__":
    main()
