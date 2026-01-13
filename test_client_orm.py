from dal.database import SessionLocal
from dal.models import Client


def main():
    with SessionLocal() as db:
        clients = db.query(Client).limit(3).all()
        for c in clients:
            print(c.cli_id, c.cli_nom, c.cli_prenom, c.cli_mail)


if __name__ == "__main__":
    main()
