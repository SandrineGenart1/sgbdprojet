from datetime import date, timedelta
from dal.database import SessionLocal
from dal.repository import LocaMatRepository
from bll.location_service import LocationService

def main():
    debut = date.today()
    fin = debut + timedelta(days=1)   # 2 jours

    # 1) Valider une location (doit passer si le matériel est Disponible)
    with SessionLocal() as session:
        repo = LocaMatRepository(session)
        service = LocationService(repo)

        contrat, materiels, prix_detail = repo.transaction_valider_location(
            client_id=1,
            materiel_ids=[2],
            date_debut=debut,
            date_fin=fin,
            nb_jours=2,
            pricing_callback=service.calculer_prix
        )

        print("CONTRAT ID:", contrat.cont_id)
        print("STATUT EN FIN DE TRANSACTION:", [(m.mat_id, m.mat_statut) for m in materiels])

    # 2) Vérifier dans une nouvelle session que le statut est bien enregistré en DB
    with SessionLocal() as session:
        repo = LocaMatRepository(session)
        m2 = repo.get_materiel_by_id(2)
        print("STATUT EN DB:", m2.mat_id, m2.mat_statut)

if __name__ == "__main__":
    main()
