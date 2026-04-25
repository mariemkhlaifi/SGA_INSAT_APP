import streamlit as st
from database import run_query, run_insert

# Configuration de l'interface
st.set_page_config(
    page_title="SGA-INSAT Dashboard",
    page_icon="🎓",
    layout="wide"
)

# Titre principal
st.title("🎓 SGA-INSAT : Système de Gestion de l'Apprentissage")
st.markdown("---")

# Navigation latérale
st.sidebar.title("Menu Principal")
menu = [
    "🏠 Accueil",
    "📝 Inscription Étudiant",
    "📚 Ressources par Filière (R1)",
    "🤝 Binômes Tuteur/Parrain (R2)",
    "⭐ Satisfaction par Tuteur (R3)",
    "📊 Moyenne par Matière (R4)",
    "🏢 Salles Disponibles (R5)",
    "🧑‍🎓 Tuteurs sans Parrain (R6)",
    "🏆 Top 3 Tutorés (R8)",
    "📈 Offres d'Excellence (R10)"
]
choice = st.sidebar.selectbox("Choisir une action", menu)

# --- LOGIQUE DES SECTIONS ---

if choice == "🏠 Accueil":
    st.subheader("Bienvenue sur l'interface de gestion")
    st.write("Cette application permet de gérer et d'analyser les données de tutorat de l'INSAT en temps réel.")
    st.info("Base de données connectée : Oracle XE (Utilisateur : EtudiantSGA)")

elif choice == "📝 Inscription Étudiant":
    st.header("Ajouter un nouvel étudiant")
    st.write("Remplissez le formulaire ci-dessous pour enregistrer un nouvel inscrit.")
    
    with st.form("form_etudiant"):
        col1, col2 = st.columns(2)
        with col1:
            code = st.text_input("Code INSAT (ex: 22005)")
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
        with col2:
            # Correction des niveaux selon le cursus INSAT
            niveaux_insat = ["1ère année MPI", "2ème année", "3ème année", "4ème année", "5ème année"]
            niveau = st.selectbox("Année d'étude", niveaux_insat)
            
            # Récupération dynamique des départements depuis la base
            df_dep = run_query("SELECT code_depar FROM departement")
            dep_list = df_dep['CODE_DEPAR'].tolist() if df_dep is not None else ["GL", "RT", "IIA", "IMI"]
            dep = st.selectbox("Filière / Département", dep_list)
        
        submitted = st.form_submit_button("Enregistrer l'étudiant")
        
        if submitted:
            if code and nom and prenom:
                sql = "INSERT INTO etudiant_ (code_insat, nom, prenom, niveau, code_depar) VALUES (:1, :2, :3, :4, :5)"
                success = run_insert(sql, (code, nom, prenom, niveau, dep))
                if success:
                    st.success(f"L'étudiant {prenom} {nom} a été ajouté avec succès !")
                    st.balloons()
            else:
                st.warning("Veuillez remplir tous les champs obligatoires.")

# --- Garder les autres sections (R1, R2, etc.) comme tu les as écrites ---
elif choice == "📚 Ressources par Filière (R1)":
    st.header("Ressources pédagogiques (IIA)")
    query = """
        SELECT rp.titre AS "Titre", rp.type_ressource AS "Type", m.Libelle AS "Matière"
        FROM ressource_pedagogique rp
        JOIN offre_tutorat ot ON rp.id_offre = ot.id_offre
        JOIN matiere m ON ot.code_matiere = m.code_matiere
        JOIN departement d ON m.code_depar = d.code_depar
        WHERE d.code_depar = 'IIA'
    """
    df = run_query(query)
    st.dataframe(df, width=1200)

elif choice == "🤝 Binômes Tuteur/Parrain (R2)":
    st.header("Binômes de départements différents")
    query = """
        SELECT j.NOM || ' ' || j.Prenom AS "Junior", dj.Nom_dept AS "Dépt Junior",
               s.NOM || ' ' || s.Prenom AS "Parrain", ds.Nom_dept AS "Dépt Parrain"
        FROM etudiant_ j
        JOIN etudiant_ s ON j.code_insat_parrain = s.code_insat
        JOIN departement dj ON j.code_depar = dj.code_depar
        JOIN departement ds ON s.code_depar = ds.code_depar
        WHERE j.code_depar <> s.code_depar
    """
    df = run_query(query)
    if df is not None and not df.empty:
        st.table(df)
    else:
        st.info("Aucun binôme mixte trouvé.")

elif choice == "📊 Moyenne par Matière (R4)":
    st.header("Satisfaction globale par matière")
    query = """
        SELECT m.Libelle AS "Matière", ROUND(AVG(si.note_satis), 2) AS "Note"
        FROM matiere m
        JOIN offre_tutorat ot ON ot.code_matiere = m.code_matiere
        JOIN s_inscrire si ON si.id_offre = ot.id_offre
        WHERE si.note_satis IS NOT NULL
        GROUP BY m.Libelle
    """
    df = run_query(query)
    if df is not None:
        st.bar_chart(data=df.set_index("Matière"))

elif choice == "🏢 Salles Disponibles (R5)":
    st.header("Salles n'ayant aucune réservation")
    query = "SELECT numero, bloc, capacite_salle FROM salle_ s LEFT JOIN offre_tutorat ot ON ot.id_salle = s.id_salle WHERE ot.id_salle IS NULL"
    df = run_query(query)
    st.dataframe(df)

elif choice == "🏆 Top 3 Tutorés (R8)":
    st.header("Top 3 des étudiants les plus assidus")
    query = """
        SELECT * FROM (
            SELECT e.NOM || ' ' || e.Prenom AS "Etudiant", COUNT(si.id_offre) AS "Inscriptions"
            FROM etudiant_ e
            JOIN s_inscrire si ON si.code_insat = e.code_insat
            GROUP BY e.NOM, e.Prenom
            ORDER BY 2 DESC
        ) WHERE ROWNUM <= 3
    """
    df = run_query(query)
    st.table(df)

elif choice == "📈 Offres d'Excellence (R10)":
    st.header("Offres dépassant la moyenne générale")
    query = """
        SELECT ot.id_offre, m.Libelle, ROUND(AVG(si.note_satis), 2) AS "Note"
        FROM offre_tutorat ot
        JOIN matiere m ON ot.code_matiere = m.code_matiere
        JOIN s_inscrire si ON si.id_offre = ot.id_offre
        GROUP BY ot.id_offre, m.Libelle
        HAVING AVG(si.note_satis) > (SELECT AVG(note_satis) FROM s_inscrire)
    """
    df = run_query(query)
    st.dataframe(df)