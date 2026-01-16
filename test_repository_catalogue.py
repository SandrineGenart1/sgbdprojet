"""
Test minimal du Repository (lecture catalogue).

Objectif :
- vérifier qu'on sait instancier le repository avec une session
- vérifier que les requêtes SELECT fonctionnent via select(...)
"""

from dal.database import SessionLocal
from dal.repository import LocaMatRepository


def main():
    with SessionLocal() as session:
        repo = LocaMatRepository(session)

        categories = repo.get_all_categories()
        print("CATEGORIES:", len(categories))
        for c in categories:
            print(c.cat_id, c.cat_libelle)

        marques = repo.get_all_marques()
        print("MARQUES:", len(marques))
        for m in marques:
            print(m.mar_id, m.mar_libelle)


if __name__ == "__main__":
    main()
