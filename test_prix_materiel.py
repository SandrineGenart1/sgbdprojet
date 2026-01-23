from dal.database import SessionLocal
from dal.repository import LocaMatRepository

def main():
    with SessionLocal() as session:
        repo = LocaMatRepository(session)

        materiels = repo.get_all_materiels()

        print("ID | STATUT | PRIX/JOUR")
        print("-----------------------")
        for m in materiels[:5]:   # on limite à 5 pour la lisibilité
            print(m.mat_id, m.mat_statut, m.mat_prix_jour)

if __name__ == "__main__":
    main()
