# Reddit Scraper avec Playwright & MongoDB

## Description

Ce projet est un scraper Reddit automatisé écrit en Python.
Il permet de collecter des posts Reddit récents à partir d’une requête de recherche
et de stocker les données dans une base MongoDB.

---

## Technologies utilisées

- Python 3
- Playwright (Chromium)
- MongoDB Atlas
- pymongo
- JSON (cookies Reddit)

---

## Fonctionnalités principales

- Recherche de posts Reddit via une URL personnalisée
- Navigation automatisée avec Playwright
- Chargement de cookies pour éviter les blocages
- Scroll dynamique pour charger le contenu
- Extraction :
  - du titre du post
  - du contenu
  - des commentaires imbriqués
- Insertion des données dans MongoDB

---

## Configuration

Les paramètres principaux sont définis au début du script :

- URL de recherche Reddit
- Chemin vers le fichier de cookies
- URI MongoDB
- Nom de la base de données
- Nom de la collection

---

## Gestion des cookies

Le script charge des cookies Reddit existants depuis un fichier `cookies.json`
afin de simuler une session utilisateur authentifiée.

Sans cookies valides, Reddit bloque rapidement l’accès (CAPTCHA ou pages vides).

---

## Extraction des commentaires

Les commentaires sont extraits de manière récursive.
Chaque commentaire est stocké avec :
- son texte
- son niveau de profondeur dans la discussion

Cela permet de conserver la structure complète des threads Reddit.

---

## Stockage MongoDB

Chaque post est stocké sous forme de document MongoDB contenant :
- URL de recherche
- URL du post
- date de scraping
- contenu du post
- liste des commentaires
- nombre total de commentaires

---

## Limitations

- Pas de déduplication des posts
- Dépend fortement du DOM de Reddit
- Sensible aux changements d’interface
- Navigation non headless
- Risque de blocage si usage intensif

Ce projet n’est pas conçu pour un usage industriel.

---

## Lancement du script

```bash
python test.py
