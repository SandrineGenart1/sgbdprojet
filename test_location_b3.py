from datetime import date
from dal.database import SessionLocal
from dal.repository import LocaMatRepository
from bll.location_service import LocationService

def main():
    # Session 1 : tester client_est_risque
    with SessionLocal() as session:
        repo = LocaMatRepository(session)
        risque = repo.client_est_risque(1)
        print("CLIENT 1 RISQUE ?", risque)

    # Session 2 : tester transaction_valider_location
    with SessionLocal() as session:
        repo = LocaMatRepository(session)
        service = LocationService(repo)

        client, materiels, prix_detail = repo.transaction_valider_location(
            client_id=1,
            materiel_ids=[2],
            date_debut=date.today(),
            date_fin=date.today(),
            nb_jours=1,
            pricing_callback=service.calculer_prix
        )

        print("CLIENT:", client.cli_id, "VIP:", client.cli_vip)
        print("MATERIELS:", [m.mat_id for m in materiels])
        print("PRIX:", prix_detail)

if __name__ == "__main__":
    main()
