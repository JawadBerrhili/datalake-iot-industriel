# Captures d'écran du projet

Ce dossier rassemble les captures qui documentent et montrent chaque étape du
projet, de l'analyse des données (C18) à la gouvernance (C21). Les fichiers
sont numérotés selon le déroulé du projet : un tri par nom les affiche dans
l'ordre logique.

## C18 — Analyse et architecture

- **01_analyse_recap_colonnes_5_fichiers.png**
  Sortie du script d'exploration. Montre les colonnes des 5 fichiers et met en
  évidence l'hétérogénéité de départ : la colonne elapsed_time est présente sur
  les lignes A et B, absente sur C, D et E.

- **02_architecture_schema.png**
  Schéma technique de l'architecture. Flux raw → staging → curated, archive
  alimentée par la règle ILM, et couche transverse de gouvernance et sécurité.

## C19 — Stockage et pipelines

- **03_stockage_minio_raw_partitionnement.png**
  Console MinIO, bucket raw. Montre le partitionnement des données par ligne
  (line=lineA, line=lineB, ...), et le bucket en accès privé.

- **04a_pipelines_airflow_vue_dags.png**
  Vue d'ensemble Airflow : les deux DAGs (ingestion_raw et
  transformation_staging), actifs et exécutés avec succès.

- **04b_pipelines_airflow_dag_ingestion_raw.png**
  Détail du DAG d'ingestion : une tâche par ligne (ingest_lineA à E), toutes
  au vert.

- **04c_pipelines_airflow_dag_transformation_staging.png**
  Détail du DAG de transformation : une tâche par ligne (transform_lineA à E),
  toutes au vert. C'est ce DAG qui harmonise les schémas.

## C20 — Catalogue OpenMetadata

- **05_catalogue_openmetadata_vue_ensemble.png**
  Vue d'ensemble du catalogue : les jeux de données de la couche staging,
  catalogués et documentés.

- **06a_catalogue_openmetadata_fiche_lineA.png**
  Fiche documentée de la ligne A : description, propriétaire, colonnes et sens
  du champ label.

- **06b_catalogue_openmetadata_fiche_lineB.png**
  Fiche documentée de la ligne B (elapsed_time présent à la source).

- **06c_catalogue_openmetadata_fiche_lineC.png**
  Fiche documentée de la ligne C. La colonne elapsed_time est documentée comme
  vide (ajoutée à l'harmonisation car absente à la source).

- **06d_catalogue_openmetadata_fiche_lineD.png**
  Fiche documentée de la ligne D (elapsed_time vide, même cas que C).

- **06e_catalogue_openmetadata_fiche_lineE.png**
  Fiche documentée de la ligne E (elapsed_time vide, même cas que C).

## C21 — Gouvernance et sécurité

- **08_gouvernance_matrice_3_comptes.png**
  Liste des trois comptes de service et de leur police attachée : data-admin
  (consoleAdmin), data-analyst, data-engineer. C'est la matrice des droits.

- **09_gouvernance_test_data-analyst_refus_raw.png**
  Test du moindre privilège. Le data-analyst peut lister curated mais se voit
  refuser l'écriture dans raw (Insufficient permissions).

- **10_gouvernance_test_data-engineer.png**
  Test du moindre privilège. Le data-engineer écrit dans raw et staging, mais
  se voit refuser curated.

- **11_gouvernance_chiffrement_sse-s3_et_ilm.png**
  Métadonnées d'un objet déposé dans raw : Encryption: SSE-S3 (chiffrement au
  repos actif) et Expiration (règle ILM de suppression à 2 ans).

- **12_gouvernance_audit_trace_acces.png**
  Session d'audit capturée en temps réel : accès autorisés (200 OK) et accès
  refusés (403 Forbidden), dont une tentative d'écriture bloquée. Illustre le
  principe prévenir et détecter.
