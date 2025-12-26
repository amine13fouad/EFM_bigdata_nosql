import streamlit as st
import pandas as pd
from pymongo import MongoClient
import certifi
import subprocess

# =====================================================
# CONFIGURATION GÉNÉRALE
# =====================================================

MONGO_URI = "mongodb+srv://amine13fouad:aqw123zsx456@efmbigdata.h8tofnj.mongodb.net/"

st.set_page_config(
    page_title="Tableau de bord – Analyse Reddit",
    layout="wide"
)

# =====================================================
# CONNEXION MONGODB
# =====================================================

client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
db = client["EFMBIGDATA"]

edges_col = db["reddit_edges"]
metrics_col = db["reddit_user_metrics"]
communities_col = db["reddit_user_communities"]
sentiment_col = db["reddit_sentiment"]
community_summary_col = db["reddit_community_summary"]

# =====================================================
# UTILITAIRE POUR LANCER DES SCRIPTS
# =====================================================

def run_script(script_path: str):
    try:
        subprocess.run(
            ["python", script_path],
            check=True
        )
        return True
    except Exception as e:
        st.error(f"❌ Erreur lors de l’exécution de {script_path}")
        return False

# =====================================================
# TITRE
# =====================================================

st.title("📊 Tableau de bord – Analyse des réseaux sociaux Reddit")
st.caption("Projet Big Data & NoSQL – Analyse des interactions, communautés et sentiments")

# =====================================================
# BOUTONS D’ACTIONS (RECALCULS)
# =====================================================

st.subheader("🔄 Recalcul des analyses")

b1, b2, b3, b4, b5 = st.columns(5)

with b1:
    if st.button("🔗 Recalculer les arêtes"):
        if run_script("graph_processing/build_edges.py"):
            st.success("Arêtes recalculées avec succès")

with b2:
    if st.button("📐 Recalculer les métriques SNA"):
        if run_script("graph_processing/compute_metrics.py"):
            st.success("Métriques du réseau recalculées")

with b3:
    if st.button("🏘️ Recalculer les communautés"):
        ok1 = run_script("graph_processing/detect_communities.py")
        ok2 = run_script("graph_processing/summarize_communities.py")
        if ok1 and ok2:
            st.success("Communautés recalculées")

with b4:
    if st.button("😊 Recalculer le sentiment"):
        if run_script("sentiment_analysis/compute_sentiment_vader.py"):
            st.success("Analyse de sentiment recalculée")

with b5:
    if st.button("🔄 Rafraîchir l’affichage"):
        st.rerun()

st.divider()

# =====================================================
# CHARGEMENT DES DONNÉES
# =====================================================

edges_count = edges_col.count_documents({})
df_metrics = pd.DataFrame(list(metrics_col.find({}, {"_id": 0})))
df_communities = pd.DataFrame(list(communities_col.find({}, {"_id": 0})))
df_sentiment = pd.DataFrame(list(sentiment_col.find({}, {"_id": 0})))
df_summary = pd.DataFrame(list(community_summary_col.find({}, {"_id": 0})))

# =====================================================
# INDICATEURS GLOBAUX
# =====================================================

st.subheader("📌 Indicateurs globaux")

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Nombre d’arêtes", edges_count)
k2.metric("Utilisateurs", len(df_metrics))
k3.metric(
    "Communautés",
    df_communities["community"].nunique() if not df_communities.empty else 0
)
k4.metric("Documents de sentiment", len(df_sentiment))
k5.metric(
    "Posts analysés",
    df_sentiment[df_sentiment["level"] == "post"].shape[0]
)

st.divider()

# =====================================================
# ANALYSE DE SENTIMENT
# =====================================================

st.subheader("😊 Analyse de sentiment des commentaires")

if not df_sentiment.empty:
    df_comments = df_sentiment[df_sentiment["level"] == "comment"]
    sentiment_counts = df_comments["label"].value_counts()
    st.bar_chart(sentiment_counts)
else:
    st.info("Aucune donnée de sentiment disponible.")

st.divider()

# =====================================================
# ANALYSE DU RÉSEAU SOCIAL
# =====================================================

st.subheader("👥 Analyse du réseau social")

left, right = st.columns(2)

with left:
    st.markdown("### 🔥 Utilisateurs les plus influents")
    if not df_metrics.empty:
        st.dataframe(
            df_metrics
            .sort_values("weighted_in_degree", ascending=False)
            .head(10)[["user", "weighted_in_degree"]]
        )
    else:
        st.info("Aucune métrique disponible.")

with right:
    st.markdown("### 🌉 Utilisateurs passerelles (betweenness)")
    if not df_metrics.empty:
        st.dataframe(
            df_metrics
            .sort_values("betweenness", ascending=False)
            .head(10)[["user", "betweenness"]]
        )
    else:
        st.info("Aucune métrique disponible.")

st.divider()

# =====================================================
# COMMUNAUTÉS
# =====================================================

st.subheader("🏘️ Structure des communautés")

if not df_communities.empty:
    st.markdown("### Répartition des communautés")
    st.bar_chart(df_communities["community"].value_counts())

if not df_summary.empty:
    st.markdown("### Détails des principales communautés")
    for _, row in df_summary.sort_values("size", ascending=False).head(5).iterrows():
        st.markdown(f"**Communauté {row['community']} – {row['size']} utilisateurs**")
        st.table(pd.DataFrame(row["top_influential"]))

st.divider()

