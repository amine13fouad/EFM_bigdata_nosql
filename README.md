Reddit Scraper avec Playwright & MongoDB
📌 Description

Ce projet est un scraper Reddit automatisé écrit en Python.
Il permet de :

Rechercher des posts Reddit via une URL de recherche donnée

Ouvrir chaque post trouvé

Extraire :

le titre

le contenu du post

l’ensemble des commentaires, y compris les réponses imbriquées

Stocker les données dans une base MongoDB (MongoDB Atlas)

⚠️ Ce script n’utilise pas l’API officielle de Reddit. Il repose sur un navigateur automatisé (Playwright) avec cookies pour éviter les blocages.

Le fonctionnement et la structure décrits ci-dessous sont directement basés sur le fichier source 

test

.

🛠️ Technologies utilisées

Python 3

Playwright (Chromium) – automatisation du navigateur

MongoDB / MongoDB Atlas

pymongo – connexion et insertion de données

JSON – gestion des cookies

Reddit Web (DOM scraping)

📂 Structure du script

Le script est organisé en plusieurs sections claires :

├── Configuration
├── Connexion MongoDB
├── Gestion des cookies
├── Fonctions utilitaires (scroll, extraction)
├── Scraping des posts
└── Boucle principale

⚙️ Configuration

Les paramètres principaux sont définis en haut du fichier :

SEARCH_URL = "https://www.reddit.com/search/?q=caf+morocco&type=posts&sort=new"
COOKIE_PATH = "cookies.json"

MONGO_URI = "mongodb+srv://..."
DB_NAME = "EFMBIGDATA"
COLLECTION_NAME = "reddit_posts"

Explication :

SEARCH_URL : URL de recherche Reddit (modifiable selon le mot-clé)

COOKIE_PATH : fichier contenant les cookies Reddit exportés

MONGO_URI : URI de connexion MongoDB Atlas

DB_NAME / COLLECTION_NAME : base et collection cibles

🍪 Gestion des cookies Reddit

Reddit bloque rapidement les scrapers non authentifiés.
Ce script charge donc des cookies existants via :

load_cookies(context)

Fonctionnement :

Lecture du fichier cookies.json

Normalisation du format des cookies

Injection dans le contexte Playwright avant toute navigation

⚠️ Sans cookies valides :

CAPTCHA

pages vides

blocage complet du scraping

🔄 Scroll dynamique

Reddit charge les posts et commentaires dynamiquement.

La fonction :

scroll_until_loaded(page)


Scroll automatiquement la page

Attend que la hauteur du DOM cesse d’augmenter

Évite de scraper des pages partiellement chargées

💬 Extraction des commentaires (récursive)

Le point le plus important du script est l’extraction hiérarchique des commentaires.

Fonction clé :
extract_comments(comment_element, depth=0)

Ce qu’elle fait :

Récupère le texte du commentaire

Stocke le niveau de profondeur (depth)

Appelle récursivement les réponses imbriquées

Structure finale d’un commentaire :
{
  "depth": 2,
  "text": "Contenu du commentaire"
}


Cela permet :

une analyse de threads

un traitement NLP ultérieur

une reconstruction de l’arbre de discussion

📝 Scraping d’un post Reddit

La fonction :

scrape_post(page)


Récupère :

Titre du post

Contenu textuel

Tous les commentaires

Nombre total de commentaires extraits

Retourne un dictionnaire structuré prêt à être inséré en base.

🗄️ Stockage MongoDB

Chaque post est inséré sous forme de document :

{
  "search_url": "...",
  "post_url": "...",
  "scraped_at": "UTC datetime",
  "title": "...",
  "content": "...",
  "comments": [...],
  "comment_count": 42
}


📌 L’insertion se fait post par post, sans mise à jour ni déduplication.

▶️ Boucle principale

Le script :

Ouvre Reddit via Playwright

Charge les cookies

Charge la page de recherche

Parcourt chaque post trouvé

Scrape le contenu

Insère dans MongoDB

Retourne à la page de recherche

Continue jusqu’à épuisement des posts
