from dal.database import SessionLocal
from dal.repository import LocaMatRepository
from bll.catalogue_service import CatalogueService


def main():
    # On ouvre une session (technique)
    with SessionLocal() as session:
        # On instancie le repository avec la session (DAL)
        repo = LocaMatRepository(session)

        # On injecte le repository dans le service (BLL)
        service = CatalogueService(repo)

        # On utilise la BLL
        dispo = service.lister_materiels_disponibles()

        print(f"DISPONIBLES: {len(dispo)}")
        for m in dispo:
            print(m.mat_id, m.mat_serial, m.mat_statut)


if __name__ == "__main__":
    main()
