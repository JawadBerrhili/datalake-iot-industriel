# Data Lake IoT industriel

Projet de mise en place d'un data lake pour centraliser et gouverner les
données de capteurs de cinq lignes de production industrielles, dans la
perspective d'un futur projet de maintenance prédictive.

Réalisé dans le cadre du titre Data Engineer (épreuve E7).

## Objectif

Centraliser, documenter et sécuriser des données aujourd'hui dispersées
et hétérogènes, en construisant un data lake organisé en couches.

## Stack technique

- MinIO (stockage objet, compatible S3)
- Airflow (orchestration des pipelines)
- OpenMetadata (catalogue de données)
- Python / boto3
- Docker Compose
- Git

## Architecture

Le data lake est organisé en quatre couches : raw, staging, curated et
archive. Le schéma complet est dans docs/architecture.pdf.

## Structure du dépôt

- data/       : les fichiers CSV sources (non versionnés, voir le script)
- scripts/    : scripts Python (téléchargement, exploration, upload)
- dags/       : les DAGs Airflow
- docs/       : analyse des données, architecture, gouvernance
- docker/     : fichiers Docker Compose

## Reproduire l'environnement

1. Cloner le dépôt
2. Créer l'environnement virtuel : `python3 -m venv venv`
3. L'activer : `source venv/bin/activate`
4. Installer les dépendances : `pip install -r requirements.txt`
5. Télécharger les données : `python scripts/download_data.py`
