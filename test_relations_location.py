from dal.database import SessionLocal
from dal.models import LigneContrat


def main():
    with SessionLocal() as db:
        lignes = db.query(LigneContrat).limit(5).all()
        for lc in lignes:
            print(
                "Contrat:", lc.contrat.cont_id,
                "| Client:", lc.contrat.client.cli_nom, lc.contrat.client.cli_prenom,
                "| Materiel:", lc.materiel.mat_serial,
                "| Modele:", lc.materiel.modele.mod_libelle
            )


if __name__ == "__main__":
    main()
