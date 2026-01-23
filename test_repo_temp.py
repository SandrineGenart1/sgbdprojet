from dal.database import SessionLocal
from dal.repository import LocaMatRepository

def main():
    with SessionLocal() as session:
        repo = LocaMatRepository(session)

        print("=== CLIENTS ===")
        clients = repo.get_all_clients()
        print(len(clients))

        print("=== MATERIELS PAR IDS ===")
        materiels = repo.get_materiels_by_ids([1, 2, 3])
        for m in materiels:
            print(m.mat_id, m.mat_serial, m.mat_statut)

     
        print("=== MATERIELS FOR UPDATE (transaction) ===")
        session.rollback()          # ✅ AJOUTE CETTE LIGNE
        with session.begin():
            locked = repo.get_materiels_by_ids_for_update([1])
            print(locked[0].mat_id, locked[0].mat_statut)

if __name__ == "__main__":
    main()
