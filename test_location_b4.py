from datetime import date, timedelta
from dal.database import SessionLocal
from dal.repository import LocaMatRepository
from bll.location_service import LocationService

def main():
    with SessionLocal() as session:
        repo = LocaMatRepository(session)
        service = LocationService(repo)

        debut = date.today()
        fin = debut + timedelta(days=2)

        contrat, materiels, prix_detail = repo.transaction_valider_location(
            client_id=1,
            materiel_ids=[2],  # dispo
            date_debut=debut,
            date_fin=fin,
            nb_jours=3,
            pricing_callback=service.calculer_prix
        )

        print("CONTRAT ID:", contrat.cont_id)
        print("CLIENT ID:", contrat.cli_id)
        print("DATES:", contrat.cont_dateDebut, "->", contrat.cont_dateFin)
        print("MATERIELS:", [m.mat_id for m in materiels])
        print("PRIX:", prix_detail)

if __name__ == "__main__":
    main()
