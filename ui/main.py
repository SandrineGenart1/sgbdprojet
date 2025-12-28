from dal.db import get_connection

def main():
    print("Test de connexion à la base de données")

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                resultat = cur.fetchone()[0]
                print("Connexion OK, résultat =", resultat)

    except Exception as e:
        print("Erreur de connexion :", e)

if __name__ == "__main__":
    main()
