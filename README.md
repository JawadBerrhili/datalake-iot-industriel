# Data Lake IoT industriel

Projet de mise en place d'un data lake pour centraliser et gouverner les
données de capteurs de cinq lignes de production industrielles, dans la
perspective d'un futur projet de maintenance prédictive.

Réalisé dans le cadre du titre Data Engineer (épreuve E7).

## Objectif

Centraliser, documenter et sécuriser des données aujourd'hui dispersées
et hétérogènes, en construisant un data lake organisé en couches, catalogué
et gouverné.

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

Le détail de l'analyse, des choix d'architecture et de la gouvernance est
dans le dossier docs/ :
- docs/01_analyse_donnees.md : analyse des 5 fichiers et des écarts de schéma
- docs/02_architecture.md : architecture en couches et justification des choix
- docs/03_policies_initiales.md : principe d'accès aux buckets
- docs/05_fiches_metadonnees.md : contenu des 5 fiches de métadonnées
- docs/06_problemes_rencontres.md : obstacles rencontrés et solutions
- docs/07_regles_cycle_de_vie.md : règles de cycle de vie (ILM)
- docs/08_politique_gouvernance.md : matrice des droits et gouvernance
- docs/architecture.pdf : schéma technique annoté
- docs/captures/ : captures d'écran (catalogue, tests de gouvernance)

## Structure du dépôt

- data/       : les fichiers CSV sources (non versionnés, voir le script)
- scripts/    : scripts Python (téléchargement, exploration, upload)
- dags/       : les DAGs Airflow (ingestion, transformation)
- docs/       : analyse, architecture, gouvernance, captures, schéma
- docker/     : docker-compose.yml (MinIO + Airflow) et policies/ (droits JSON)
- openmetadata/ : docker-compose.yml du catalogue OpenMetadata

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
- Airflow (orchestration) : interface sur http://localhost:8081

Identifiants MinIO : minioadmin / minioadmin

Mot de passe Airflow :

    docker exec airflow cat /opt/airflow/standalone_admin_password.txt

Note : Airflow est exposé sur le port 8081 (et non 8080) pour laisser le
port 8080 à OpenMetadata, qui embarque son propre Airflow interne.

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

## 8. Démarrer le catalogue OpenMetadata

    cd openmetadata
    docker compose up -d

OpenMetadata démarre (4 conteneurs). Prévoir quelques minutes.
Interface : http://localhost:8585 (admin@open-metadata.org / admin)

Pour que le catalogue communique avec MinIO, les deux stacks sont reliées
par un réseau Docker partagé :

    docker network create datalake-shared

Ce réseau est déclaré comme externe dans les deux docker-compose. Un
connecteur DataLake pointe vers MinIO (endpoint http://minio:9000), scanne
les buckets, et crée une fiche par fichier. Les 5 fiches de la couche
staging sont ensuite documentées à la main (voir docs/captures/).

## 9. Gouvernance (MinIO)

La gouvernance est mise en place via le client mc, dans le conteneur MinIO :

    docker exec -it minio sh
    mc alias set local http://localhost:9000 minioadmin minioadmin

- Trois comptes de service aux droits différenciés (voir docker/policies/) :
  data-analyst (lecture curated), data-engineer (lecture/écriture raw et
  staging), data-admin (tous droits).
- Chiffrement SSE-S3 activé sur raw et staging (via le KMS interne de MinIO,
  clé dans docker/.env non versionné).
- Règle de cycle de vie : expiration après 2 ans (voir
  docs/07_regles_cycle_de_vie.md).
- Logs d'audit consultables via mc admin trace local.

## Résultat attendu

- Bucket raw : les 5 CSV bruts, partitionnés et chiffrés
- Bucket staging : les 5 CSV harmonisés, tous avec le même schéma
  (timestamp, temperature, pressure, elapsed_time, label)
- Catalogue OpenMetadata : 5 fiches documentées
- Gouvernance : 3 comptes testés, chiffrement actif, audit tracé

## Arrêter l'infrastructure

    cd docker
    docker compose down
    cd ../openmetadata
    docker compose down

Les données MinIO sont conservées (volume minio-data) et restent
disponibles au prochain démarrage.
