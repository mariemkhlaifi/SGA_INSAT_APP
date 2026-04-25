import streamlit as st
from database import run_query

# Configuration de l'interface
st.set_page_config(
    page_title="SGA-INSAT Dashboard",
    page_icon="🎓",
    layout="wide"
)

# Style CSS personnalisé pour le titre
st.markdown("""
    <style>
    .main-title {
        font-size:40px !important;
        color: #1E3A8A;
        text-align: center;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">🎓 SGA-INSAT : Système de Gestion de l\'Apprentissage</p>', unsafe_allow_html=True)
st.markdown("---")

# Navigation latérale
st.sidebar.image("https://www.insat.rnu.tn/assets/images/logo.png", width=150) # Optionnel : logo INSAT si tu as l'URL
st.sidebar.title("Menu Principal")
menu = [
    "🏠 Accueil",
    "📚 Ressources par Filière (R1)",
    "🤝 Binômes Tuteur/Parrain (R2)",
    "⭐ Satisfaction par Tuteur (R3)",
    "📊 Moyenne par Matière (R4)",
    "🏢 Salles Disponibles (R5)",
    "🧑‍🎓 Tuteurs sans Parrain (R6)",
    "❌ Offres sans Ressources (R7)",
    "🏆 Top 3 Tutorés (R8)",
    "📖 Tuteurs Multi-matières (R9)",
    "📈 Offres d'Excellence (R10)"
]
choice = st.sidebar.selectbox("Choisir une analyse", menu)

# --- LOGIQUE DES SECTIONS ---

if choice == "🏠 Accueil":
    st.subheader("Bienvenue sur l'interface d'administration")
    st.write("Cette application Python est connectée en temps réel à votre base Oracle XE.")
    st.success("Connexion établie avec l'utilisateur : EtudiantSGA")
    
    # Petit résumé rapide
    col1, col2 = st.columns(2)
    with col1:
        st.info("💡 **Conseil :** Utilisez le menu à gauche pour naviguer entre les requêtes du cahier des charges.")
    with col2:
        st.warning("⚠️ **Note :** Les données affichées correspondent aux dernières insertions SQL effectuées.")

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
    st.dataframe(df, use_container_width=True)

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
        st.info("Aucun binôme mixte trouvé pour le moment.")

elif choice == "⭐ Satisfaction par Tuteur (R3)":
    st.header("Note moyenne de satisfaction par tuteur")
    query = """
        SELECT e.NOM || ' ' || e.Prenom AS "Tuteur", 
               COUNT(si.note_satis) AS "Nb Évals", 
               ROUND(AVG(si.note_satis), 2) AS "Note Moyenne"
        FROM etudiant_ e
        JOIN offre_tutorat ot ON ot.code_insat = e.code_insat
        JOIN s_inscrire si ON si.id_offre = ot.id_offre
        WHERE si.note_satis IS NOT NULL
        GROUP BY e.code_insat, e.NOM, e.Prenom
        ORDER BY 3 DESC
    """
    df = run_query(query)
    st.dataframe(df)

elif choice == "📊 Moyenne par Matière (R4)":
    st.header("Satisfaction globale par matière")
    query = """
        SELECT m.Libelle AS "Matiere", ROUND(AVG(si.note_satis), 2) AS "Note"
        FROM matiere m
        JOIN offre_tutorat ot ON ot.code_matiere = m.code_matiere
        JOIN s_inscrire si ON si.id_offre = ot.id_offre
        WHERE si.note_satis IS NOT NULL
        GROUP BY m.Libelle
    """
    df = run_query(query)
    if df is not None:
        st.bar_chart(data=df.set_index("Matiere"))

elif choice == "🏢 Salles Disponibles (R5)":
    st.header("Salles n'ayant aucune réservation")
    query = """
        SELECT numero, bloc, capacite_salle 
        FROM salle_ s
        LEFT JOIN offre_tutorat ot ON ot.id_salle = s.id_salle
        WHERE ot.id_salle IS NULL
    """
    df = run_query(query)
    st.dataframe(df)

elif choice == "🧑‍🎓 Tuteurs sans Parrain (R6)":
    st.header("Tuteurs indépendants (Sans parrain)")
    query = """
        SELECT NOM, Prenom, niveau 
        FROM etudiant_ 
        WHERE code_insat_parrain IS NULL 
        AND code_insat IN (SELECT code_insat FROM offre_tutorat)
    """
    df = run_query(query)
    st.table(df)

elif choice == "❌ Offres sans Ressources (R7)":
    st.header("Séances de tutorat sans support pédagogique")
    query = """
        SELECT ot.id_offre, m.Libelle, ot.date_seance
        FROM offre_tutorat ot
        JOIN matiere m ON ot.code_matiere = m.code_matiere
        WHERE ot.id_offre NOT IN (SELECT id_offre FROM ressource_pedagogique)
    """
    df = run_query(query)
    st.warning("Ces offres nécessitent l'ajout d'un document PDF.")
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

elif choice == "📖 Tuteurs Multi-matières (R9)":
    st.header("Tuteurs polyvalents (> 1 matière)")
    query = """
        SELECT e.NOM, COUNT(DISTINCT ot.code_matiere) AS "Nb Matières"
        FROM etudiant_ e
        JOIN offre_tutorat ot ON ot.code_insat = e.code_insat
        GROUP BY e.NOM
        HAVING COUNT(DISTINCT ot.code_matiere) > 1
    """
    df = run_query(query)
    st.dataframe(df)

elif choice == "📈 Offres d'Excellence (R10)":
    st.header("Offres dépassant la moyenne générale")
    query = """
        SELECT ot.id_offre, m.Libelle, ROUND(AVG(si.note_satis), 2) AS "Note Offre"
        FROM offre_tutorat ot
        JOIN matiere m ON ot.code_matiere = m.code_matiere
        JOIN s_inscrire si ON si.id_offre = ot.id_offre
        GROUP BY ot.id_offre, m.Libelle
        HAVING AVG(si.note_satis) > (SELECT AVG(note_satis) FROM s_inscrire)
    """
    df = run_query(query)
    st.balloons() # Petite animation pour célébrer l'excellence
    st.dataframe(df)