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
archive. La donnée avance d'une couche à l'autre en se raffinant.

Le détail de l'analyse des données et des choix d'architecture est dans le
dossier docs/ :
- docs/01_analyse_donnees.md : analyse des 5 fichiers et des écarts de schéma
- docs/02_architecture.md : architecture en couches et justification des choix
- docs/03_policies_initiales.md : principe d'accès aux buckets
- docs/architecture.pdf : schéma technique annoté

## Structure du dépôt

- data/       : les fichiers CSV sources (non versionnés, voir le script)
- scripts/    : scripts Python (téléchargement, exploration, upload)
- dags/       : les DAGs Airflow (ingestion, transformation)
- docs/       : analyse, architecture, gouvernance, schéma
- docker/     : docker-compose.yml (MinIO + Airflow)

---

# Procédure d'intégration

Cette procédure permet de remonter tout le pipeline depuis zéro.

## Prérequis

- Docker Desktop installé et démarré
- Python 3
- Le dépôt cloné

## 1. Préparer l'environnement local

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

## 2. Télécharger les données sources

    python scripts/download_data.py

Les 5 CSV sont téléchargés dans data/ et leur intégrité est vérifiée avec
les empreintes MD5 de la source.

## 3. Démarrer l'infrastructure (MinIO + Airflow)

    cd docker
    docker compose up -d

Deux services démarrent :
- MinIO (stockage objet) : console sur http://localhost:9001
- Airflow (orchestration) : interface sur http://localhost:8080

Identifiants MinIO : minioadmin / minioadmin

Mot de passe Airflow :

    docker exec airflow cat /opt/airflow/standalone_admin_password.txt

## 4. Créer les buckets dans MinIO

Dans la console MinIO, créer quatre buckets : raw, staging, curated,
archive. Les laisser en accès Private.

## 5. Déposer les fichiers bruts dans raw

    python scripts/upload_to_minio.py

Les 5 CSV sont déposés dans raw avec partitionnement
line=/year=/month=. L'intégrité est vérifiée à la réception.

Note : cette étape fait à la main ce que le DAG d'ingestion (étape 6)
automatise. Elle correspond à la première mise en place.

## 6. Lancer le pipeline d'ingestion (Airflow)

Dans l'interface Airflow :
1. Activer le DAG ingestion_raw
2. Le déclencher
3. Vérifier que les 5 tâches passent au vert

Ce DAG dépose chaque CSV dans raw avec partitionnement. La ligne A
(10 000 lignes) est lue par chunks pour simuler un flux réel.

## 7. Lancer le pipeline de transformation (Airflow)

Dans l'interface Airflow :
1. Activer le DAG transformation_staging
2. Le déclencher
3. Vérifier que les 5 tâches passent au vert

Ce DAG lit les fichiers depuis raw, harmonise les noms de colonnes en
minuscules, ajoute la colonne elapsed_time là où elle manque, convertit le
timestamp en date, et dépose le résultat dans staging.

## Résultat attendu

- Bucket raw : les 5 CSV bruts, partitionnés
- Bucket staging : les 5 CSV harmonisés, tous avec le même schéma
  (timestamp, temperature, pressure, elapsed_time, label)

## Arrêter l'infrastructure

    cd docker
    docker compose down

Les données MinIO sont conservées (volume minio-data) et restent
disponibles au prochain démarrage.
