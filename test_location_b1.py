from dal.database import SessionLocal
from dal.repository import LocaMatRepository

def main():
    # Test 1 : matériel disponible
    with SessionLocal() as session:
        repo = LocaMatRepository(session)
        try:
            client, materiels = repo.transaction_valider_location(
                client_id=1,
                materiel_ids=[2],   # dispo chez toi
                date_debut=None,
                date_fin=None,
                nb_jours=1,
                pricing_callback=None
            )
            print("OK B1:", client.cli_id, [m.mat_id for m in materiels])
        except Exception as e:
            print("ERREUR:", e)

    # Test 2 : matériel non disponible
    with SessionLocal() as session:
        repo = LocaMatRepository(session)
        try:
            repo.transaction_valider_location(
                client_id=1,
                materiel_ids=[1],   # loué chez toi
                date_debut=None,
                date_fin=None,
                nb_jours=1,
                pricing_callback=None
            )
            print("OK (ne devrait pas arriver)")
        except Exception as e:
            print("ERREUR ATTENDUE:", e)

if __name__ == "__main__":
    main()
