# Architecture du data lake

## Pourquoi une architecture en couches

J'organise le data lake en quatre couches : raw, staging, curated et archive.
La donnée avance d'une couche à l'autre en se nettoyant petit à petit, et je
ne touche jamais à la couche précédente. Comme ça, si une transformation se
passe mal, je peux toujours repartir de la donnée d'origine.

Chaque couche sera un bucket séparé dans MinIO. Ce ne sont pas des dossiers
sur le disque, mais bien des buckets de stockage objet.

## Le rôle de chaque couche

**raw**
J'y dépose les 5 fichiers CSV tels qu'ils arrivent de Zenodo, sans rien
changer. C'est ma source de vérité. Je garde tout, même les noms de colonnes
en désordre, parce que je ne sais pas encore ce dont le futur modèle de
maintenance prédictive aura besoin.

**staging**
C'est ici que je corrige les problèmes repérés dans mon analyse : je mets
tous les noms de colonnes en minuscules, j'ajoute la colonne elapsed_time
là où elle manque (LineC, LineD, LineE), et je convertis le timestamp en
vraie date. À la sortie, les 5 lignes ont le même schéma et peuvent enfin
être traitées ensemble.

**curated**
Données propres et prêtes à être utilisées pour l'analyse. Pour ce projet
la différence avec staging reste légère, mais je garde la séparation :
staging = propre techniquement, curated = prêt pour le métier.

**archive**
Les données trop anciennes sont déplacées ici automatiquement, grâce à une
règle de cycle de vie de MinIO (archivage après 180 jours, suppression
après 2 ans). Je ne supprime pas tout de suite, je conserve l'historique.

## Organisation dans le bucket raw

Je range les fichiers avec un partitionnement par ligne, année et mois.
Exemple :

raw/production_lines/line=lineA/year=2025/month=05/LineA_Stable_10K.csv

J'extrais le mois depuis le timestamp au lieu de l'écrire en dur, parce que
chaque fichier couvre un mois différent. Ce découpage permettra plus tard de
lire seulement une ligne ou un mois précis sans tout parcourir.

## Le parcours de la donnée

1. Les CSV sont téléchargés depuis Zenodo et déposés dans raw avec boto3.
2. Un DAG Airflow automatise ce dépôt (ingestion).
3. Un second DAG lit raw, harmonise les colonnes et écrit dans staging.
4. Les données passent ensuite en curated, prêtes pour l'analyse.
5. Les données anciennes glissent vers archive (règle ILM).

En parallèle, OpenMetadata documente tout le contenu du data lake, et les
règles d'accès, le chiffrement et les logs d'audit assurent la sécurité.

## Mes choix techniques

J'ai choisi MinIO pour le stockage parce qu'il accepte n'importe quel format,
qu'il monte en charge facilement et qu'il utilise l'API S3, qui est un
standard. Ce que j'apprends ici se réutilise tel quel avec un vrai S3 en
entreprise.

J'ai séparé les couches plutôt que tout mettre au même endroit pour pouvoir
reprendre un traitement sans perdre de données, et pour que chacun sache à
quel niveau de qualité se trouve la donnée qu'il consulte.