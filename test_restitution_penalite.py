from datetime import date
from dal.database import SessionLocal
from dal.repository import LocaMatRepository
from dal.models import LigneContrat

def main():
    # 1) Session 1 : lecture
    with SessionLocal() as session:
        repo = LocaMatRepository(session)
        lignes = repo.get_lignes_a_restituer()
        if not lignes:
            print("Aucune ligne à restituer.")
            return

        lc_id = lignes[0].lc_id
        print("LC choisi:", lc_id)

    # 2) Session 2 : écriture (transaction)
    with SessionLocal() as session:
        repo = LocaMatRepository(session)
        repo.transaction_restituer_lignes([lc_id], date.today())
        print("Restitution OK")

    # 3) Session 3 : relecture
    with SessionLocal() as session:
        lc = session.get(LigneContrat, lc_id)
        print("Après:", lc.lc_id, lc.lc_dateretourreelle, lc.lc_retard_jours, lc.lc_penalite)

if __name__ == "__main__":
    main()
