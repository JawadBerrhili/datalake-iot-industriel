# Politique de gouvernance des données

Ce document décrit les règles d'accès, de sécurité et de responsabilité
appliquées au data lake. Il complète la mise en œuvre technique (comptes,
policies, chiffrement, audit) par une vue d'ensemble organisationnelle.

## 1. Principe directeur : le moindre privilège

Chaque compte dispose uniquement des droits nécessaires à son rôle, et rien
de plus. Un utilisateur qui n'a besoin que de consulter des données n'a pas
le droit de les modifier. Ce principe limite les risques d'erreur et de
fuite de données.

## 2. Qui accède à quoi (matrice des droits)

Trois comptes de service ont été créés, avec des droits strictement
différenciés par bucket.

| Compte         | raw        | staging    | curated       | archive | Administration |
|----------------|------------|------------|---------------|---------|----------------|
| data-analyst   | aucun      | aucun      | lecture seule | aucun   | non            |
| data-engineer  | lecture/écriture | lecture/écriture | aucun | aucun | non         |
| data-admin     | tous droits| tous droits| tous droits   | tous droits | oui        |

Justification par rôle :
- Le data-analyst consulte uniquement les données prêtes à l'analyse
  (curated). Il n'a aucun accès aux données brutes ou en cours de traitement.
- Le data-engineer travaille sur les couches de traitement (raw et staging).
  Il n'accède pas à curated, réservé à la consommation.
- Le data-admin gère l'ensemble et dispose des droits d'administration
  (création de comptes, gestion des policies).

Ces droits ont été testés : chaque compte a été vérifié comme capable de
faire ce qu'il doit, et incapable de faire ce qui lui est interdit (par
exemple, un data-analyst se voit refuser l'écriture dans raw).

## 3. Sous quelles conditions (mesures de sécurité)

**Authentification.** Tout accès au data lake nécessite un compte
authentifié (identifiant et clé secrète). Aucun accès anonyme n'est autorisé :
tous les buckets sont configurés en mode privé.

**Chiffrement au repos.** Les buckets contenant des données de production
(raw et staging) sont chiffrés automatiquement en SSE-S3. Les données sont
donc illisibles sur le support physique sans la clé de chiffrement, gérée
par le KMS interne de MinIO.

**Traçabilité.** Les accès au data lake sont traçables via les logs d'audit
de MinIO. Chaque opération (lecture, écriture, tentative refusée) est
enregistrée avec son horodatage, son auteur, la ressource concernée et le
résultat. Une session d'accès a été capturée et analysée (voir
docs/audit-session.log).

**Gestion des secrets.** Les identifiants et clés sensibles ne sont jamais
versionnés dans le dépôt Git. Ils sont stockés dans un fichier .env ignoré
par Git, et le docker-compose ne contient que des références aux variables,
pas leurs valeurs.

## 4. Responsabilités par rôle

- **data-admin** : responsable de l'administration du data lake. Crée et
  gère les comptes, applique les policies, configure le chiffrement et les
  règles de cycle de vie. Garant de la sécurité globale.
- **data-engineer** : responsable de l'ingestion et de la transformation des
  données (couches raw et staging). Garant de la qualité et de
  l'harmonisation des données.
- **data-analyst** : consommateur des données prêtes (curated). Responsable
  de l'usage correct des données dans le respect de son périmètre de lecture.

## 5. Cycle de vie des données

Les données suivent une règle de cycle de vie automatique : suppression
après 2 ans (règle active). Une règle d'archivage après 180 jours est
documentée pour un déploiement en production (voir
docs/07_regles_cycle_de_vie.md).

## 6. Limites et perspectives

Cette gouvernance est mise en œuvre dans un environnement local
d'apprentissage. En production, plusieurs éléments seraient renforcés :
gestion des clés de chiffrement par un coffre-fort externe (Vault, KMS),
collecte centralisée des logs d'audit (Elasticsearch, Kibana), et rotation
régulière des secrets. Les principes (moindre privilège, chiffrement,
traçabilité) restent identiques.