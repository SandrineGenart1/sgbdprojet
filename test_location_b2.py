from datetime import date
from dal.database import SessionLocal
from dal.repository import LocaMatRepository
from bll.location_service import LocationService

def main():
    with SessionLocal() as session:
        repo = LocaMatRepository(session)
        service = LocationService(repo)

        client, materiels, prix_detail = repo.transaction_valider_location(
            client_id=1,
            materiel_ids=[2],     # dispo
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
