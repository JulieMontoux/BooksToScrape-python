# Scraper de Livres

Ce scraper extrait les données des livres du site "Books to Scrape" et enregistre les informations dans des fichiers CSV, en téléchargeant également les images de couverture.
Des schémas de statistiques seront fait se basant sur les données extraites.

## Installation

1. Assurez-vous d'avoir Python 3.10 installé sur votre système.
2. Clonez ce dépôt Git sur votre machine locale.
3. Installez les dépendances en exécutant `pip install -r requirements.txt`.

## Utilisation

Lancez le scraper en exécutant `python main.py` et admirer le travail !

## Structure des Fichiers

- Le répertoire principal contient le fichier `main.py` et `README.md`.
- Les données scrapées sont stockées dans des fichiers CSV, un par catégorie, dans le dossier `/data`.
- Les images de couverture sont téléchargées dans le sous-dossier `/images`, organisées par catégorie.
