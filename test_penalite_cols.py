from dal.database import SessionLocal
from dal.models import LigneContrat
import inspect

def main():
    path = inspect.getfile(LigneContrat)
    print("Classe importée depuis :", path)

    # Lire le fichier réellement chargé par Python
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    print("Fichier contient 'lc_retard_jours' ?", "lc_retard_jours" in content)
    print("Fichier contient 'lc_penalite' ?", "lc_penalite" in content)

    # Ce que SQLAlchemy voit dans la classe
    print("Attributs ORM connus :", [a for a in dir(LigneContrat) if a.startswith("lc_")])

    with SessionLocal() as session:
        lc = session.query(LigneContrat).order_by(LigneContrat.lc_id.desc()).first()
        print("LC_ID:", lc.lc_id)
        print("HAS lc_retard_jours ?", hasattr(lc, "lc_retard_jours"))
        print("HAS lc_penalite ?", hasattr(lc, "lc_penalite"))

if __name__ == "__main__":
    main()
