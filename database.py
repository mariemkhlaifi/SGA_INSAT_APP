import oracledb
import pandas as pd
import streamlit as st
import warnings

# Ignore les avertissements de Pandas sur SQLAlchemy
warnings.filterwarnings("ignore", category=UserWarning)

# Activation du mode Thick pour la compatibilité Oracle XE
try:
    oracledb.init_oracle_client()
except Exception as e:
    pass

def get_connection():
    """Établit la connexion avec la base Oracle XE locale."""
    try:
        conn = oracledb.connect(
            user="EtudiantSGA",
            password="system", # Ton mot de passe est bien 'system'
            dsn="localhost:1521/xe"
        )
        return conn
    except Exception as e:
        st.error(f"Erreur de connexion à Oracle : {e}")
        return None

def run_query(sql):
    """Exécute une requête SQL et retourne un DataFrame Pandas."""
    conn = get_connection()
    if conn:
        try:
            # Utilisation de la connexion pour lire le SQL
            df = pd.read_sql(sql, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Erreur SQL : {e}")
            conn.close()
            return None
    return None

def run_insert(sql, data):
    """Exécute une insertion de données avec commit."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit() # Indispensable pour valider l'ajout en base
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Erreur lors de l'insertion : {e}")
            if conn:
                conn.close()
            return False
    return False