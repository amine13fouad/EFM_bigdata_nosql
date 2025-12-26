# Analyse des Réseaux Sociaux Reddit  
**Projet Big Data & NoSQL**

## Présentation
Ce projet vise à analyser des discussions Reddit à l’aide de l’Analyse des Réseaux Sociaux (Social Network Analysis – SNA) et de l’Analyse de Sentiment.  
Les publications et commentaires Reddit sont collectés via un scraper basé sur l’interface utilisateur, stockés dans une base de données NoSQL (MongoDB), puis transformés en graphe social afin d’étudier les interactions entre utilisateurs, les communautés et les opinions exprimées.

Le projet suit une architecture Big Data modulaire séparant l’ingestion, le traitement, l’analyse et la visualisation.

---

## Technologies utilisées
- **Python**
- **MongoDB (NoSQL)**
- **NetworkX** – analyse de graphes
- **Algorithme de Louvain** – détection de communautés
- **VADER** – analyse de sentiment
- **Streamlit** – tableau de bord interactif
- **Playwright** – scraping de l’interface Reddit

---

## Structure du projet
project/
│
├── data_ingestion/
│ └── reddit_scraper_ui.py
│
├── graph_processing/
│ ├── build_edges.py
│ ├── compute_metrics.py
│ ├── detect_communities.py
│ └── summarize_communities.py
│
├── sentiment_analysis/
│ └── compute_sentiment_vader.py
│
├── visualization/
│ ├── dashboard.py
│ └── network_visualization.py
│
├── requirements.txt
└── README.md


---

## Pipeline de traitement des données

1. **Ingestion des données**  
   - Les publications et commentaires Reddit sont collectés via Playwright.
   - Les données brutes sont stockées dans MongoDB sous forme de documents JSON.

2. **Construction du graphe social**  
   - Les interactions sont modélisées sous forme d’arêtes :
     - Auteur d’un commentaire → auteur du post
     - Auteur d’une réponse → auteur du commentaire parent
   - Un graphe orienté représentant les interactions entre utilisateurs est construit.

3. **Analyse des réseaux sociaux (SNA)**  
   - Calcul des métriques de centralité (in-degree, out-degree, betweenness).
   - Identification des utilisateurs influents, actifs et passerelles.

4. **Détection des communautés**  
   - Application de l’algorithme de Louvain pour identifier les communautés d’utilisateurs.
   - Génération de résumés mettant en évidence les principaux utilisateurs par communauté.

5. **Analyse de sentiment**  
   - Analyse du sentiment des titres de posts et des commentaires à l’aide de VADER.
   - Classification des opinions en positives, neutres ou négatives.
   - Stockage des résultats dans MongoDB.

6. **Visualisation**  
   - Développement d’un tableau de bord interactif avec Streamlit.
   - Visualisation des métriques sociales, des communautés et du sentiment.
   - Boutons permettant le recalcul dynamique des analyses sans relancer le scraping.

---

## Tableau de bord
Le tableau de bord Streamlit permet de :
- Visualiser des indicateurs globaux (utilisateurs, arêtes, communautés)
- Explorer la distribution des sentiments
- Identifier les utilisateurs influents et passerelles
- Analyser la structure des communautés
- Recalculer dynamiquement les analyses à partir des données MongoDB

---

## Installation

```bash
pip install -r requirements.txt
```

## Installation

Lancer le tableau de bord

```bash
streamlit run visualization/dashboard.py
```

## Remarques
- Le tableau de bord ne relance pas le scraping Reddit.
- Les recalculs s’effectuent uniquement à partir des données existantes dans MongoDB.
- Le projet est conçu à des fins académiques et illustre les principes d’une architecture Big Data scalable.

## Collaborateurs

Ce projet a été réalisé en collaboration par :

**Imane MAAZAOUI** – Ingénieure Big Data & Business Intelligence  
  *Scraping des données Reddit, nettoyage et structuration des données, stockage NoSQL dans MongoDB, préparation des données pour les analyses et cohérence du modèle de données.*

**Mouad SEBHAOUI** – Ingénieur Intelligence Artificielle & Machine Learning  
  *Analyse de sentiment (NLP), choix et implémentation de la méthode VADER, interprétation des résultats et contribution aux analyses analytiques avancées.*

**Amine FOUAD** – Ingénieur Intelligence Artificielle & Machine Learning  
  *Conception et modélisation du graphe social, définition des interactions (edges), analyse des réseaux sociaux (centralités, utilisateurs influents et passerelles), détection des communautés (Louvain), intégration analytique MongoDB, conception du tableau de bord et coordination technique globale du projet.*

**Abdelkabir ELAZZOUZI** – Ingénieur Développement Logiciel  
  *Support au développement, intégration technique, tests et assistance à la mise en place du dashboard.*

