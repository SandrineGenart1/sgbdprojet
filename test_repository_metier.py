from dal.database import SessionLocal
from dal.repository import LocaMatRepository


def main():
    with SessionLocal() as session:
        repo = LocaMatRepository(session)

        # 1) Matériels disponibles
        dispo = repo.get_materiels_disponibles()
        print("MATERIELS DISPONIBLES:", len(dispo))
        for m in dispo[:5]:
            print(m.mat_id, m.mat_serial, m.mat_statut)

        print("-" * 40)

        # 2) Contrats du client 1 (adapte si besoin)
        contrats = repo.get_contrats_by_client(1)
        print("CONTRATS DU CLIENT 1:", len(contrats))
        for c in contrats:
            print(c.cont_id, c.cli_id, c.cont_dateDebut, c.cont_dateFin)

        print("-" * 40)

        # 3) Lignes du contrat 1 (adapte si besoin)
        lignes = repo.get_lignes_by_contrat(1)
        print("LIGNES DU CONTRAT 1:", len(lignes))
        for lc in lignes:
            # Ici on utilise les relations ORM (pas du SQL)
            print(lc.lc_id, lc.mat_id, lc.lc_dateretourprevue, lc.lc_dateretourreelle)


if __name__ == "__main__":
    main()
