import oracledb
import pandas as pd
import streamlit as st

# Activation du mode Thick pour la compatibilité Oracle XE
try:
    oracledb.init_oracle_client()
except Exception as e:
    # Si déjà initialisé, on ignore l'erreur
    pass

def get_connection():
    """Établit la connexion avec la base Oracle XE locale."""
    try:
        # Remplace bien TON_MOT_DE_PASSE ici
        conn = oracledb.connect(
            user="EtudiantSGA",
            password="system",
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
            df = pd.read_sql(sql, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Erreur SQL : {e}")
            conn.close()
            return None
    return None