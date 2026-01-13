import os
import psycopg
from dotenv import load_dotenv

# Charge les variables d’environnement depuis le fichier .env
load_dotenv()

def get_connection():
    """
    On crée une fonction qui établit une connexion à la base de données PostgreSQL
    en utilisant un utilisateur applicatif dédié.
    Les paramètres de connexion sont lus depuis le fichier .env
    afin d’éviter toute information sensible dans le code.C'est obligatoire pour la
    sécurité d'une application.
    """

    # Paramètres de connexion regroupés dans un dictionnaire
    connection_params = {
        "host": os.getenv("DB_HOST"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": os.getenv("DB_PORT")
    }

    try:
        print("Tentative de connexion à la base de données...")
        return psycopg.connect(**connection_params)

    except psycopg.Error as e:
        print("Erreur de connexion à PostgreSQL.")
        print("Détail de l’erreur :", e)
        raise  # On relance l’erreur pour qu’elle soit gérée plus haut (BLL / UI)
