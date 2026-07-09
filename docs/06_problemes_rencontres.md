# Problèmes rencontrés et solutions

Ce document liste les difficultés techniques rencontrées pendant le projet
et la façon dont je les ai résolues. Il sert de mémoire pour la restitution
et le rapport final.

## 1. Conflit de port entre mon Airflow et OpenMetadata

**Problème.** OpenMetadata embarque son propre module d'ingestion, qui est
en fait un Airflow interne tournant sur le port 8080. Or mon propre Airflow
utilisait déjà ce port 8080. Les deux ne pouvaient pas coexister.

**Solution.** J'ai déplacé mon Airflow sur le port 8081 côté machine, en
modifiant le mapping de ports dans mon docker-compose (8081:8080). Le port
interne du conteneur reste 8080, seule la porte d'accès depuis ma machine
change. Cela a libéré le 8080 pour OpenMetadata. J'accède désormais à mon
Airflow via localhost:8081.

## 2. Communication entre deux docker-compose séparés

**Problème.** J'ai choisi de garder OpenMetadata dans son propre
docker-compose, séparé de celui qui contient MinIO et Airflow. Par défaut,
deux docker-compose créent deux réseaux isolés qui ne se voient pas. Or
OpenMetadata devait pouvoir communiquer avec MinIO pour cataloguer les
données.

**Solution.** J'ai créé un réseau Docker partagé (datalake-shared) avec la
commande docker network create. J'ai ensuite branché MinIO et le service
d'ingestion d'OpenMetadata sur ce réseau commun, en le déclarant comme
réseau externe dans les deux fichiers. OpenMetadata peut alors joindre
MinIO par son nom de service (http://minio:9000).

## 3. Elasticsearch arrêté par manque de mémoire

**Problème.** Après le premier scan, la page Explore d'OpenMetadata
affichait une erreur Elasticsearch et ne montrait aucun résultat. En
vérifiant les conteneurs, j'ai constaté que le conteneur Elasticsearch
avait disparu : il avait été arrêté par manque de mémoire (plusieurs
conteneurs lourds tournaient en même temps).

**Solution.** J'ai relancé Elasticsearch avec docker compose up -d, qui
recrée le conteneur manquant. Pour éviter que le problème se reproduise,
j'ai mis mon Airflow en pause pendant le travail sur OpenMetadata, car je
n'en avais pas besoin à ce moment-là. Cela a libéré de la mémoire pour
Elasticsearch.

## 4. Index de recherche vide dans OpenMetadata

**Problème.** Une fois Elasticsearch relancé, il était vide : il avait perdu
son index en s'arrêtant. La page Explore ne trouvait donc toujours rien,
alors que le scan avait bien réussi et que les données étaient présentes
dans la base.

**Solution.** J'ai lancé une réindexation depuis les paramètres
d'OpenMetadata (Settings > Applications > Search Indexing). Cette opération
recopie les données de la base vers le moteur de recherche. Après quelques
minutes, mes fichiers sont apparus dans Explore.

## 5. Fichiers présents en double dans le catalogue

**Problème.** Le scan d'OpenMetadata avait ratissé tous les buckets, sans
filtre. Mes fichiers apparaissaient donc en double : une version dans raw
(colonnes non harmonisées) et une version dans staging (colonnes
harmonisées).

**Solution.** J'ai documenté uniquement les fichiers du bucket staging, qui
contient les données propres et harmonisées, celles qu'un analyste
consommerait. J'ai laissé les versions raw dans le catalogue sans les
documenter, car cataloguer raw et staging reste cohérent avec l'architecture
en couches.

## 6. Règle d'archivage ILM impossible en local (transition de tier)

**Problème.** Le brief demande un archivage automatique après 180 jours.
Dans MinIO, cet archivage correspond à une règle de transition, qui déplace
les objets vers un tier de stockage distinct. Or une transition exige qu'un
tier de destination soit configuré. J'ai essayé de créer un tier pointant
vers mon propre serveur MinIO (bucket archive), mais la commande restait
bloquée : en local, sur un seul nœud, MinIO n'arrive pas à se connecter à
lui-même proprement pour ce type de configuration.

**Solution.** J'ai implémenté la règle qui fonctionne nativement :
l'expiration automatique après 2 ans (730 jours), qui supprime les objets
anciens sans nécessiter de tier. Pour l'archivage à 180 jours, je l'ai
documenté comme règle de cycle de vie prévue, applicable en environnement
de production où un tier de stockage distant est disponible. Cela montre que
j'ai compris la mécanique ILM et ses contraintes réelles selon
l'environnement.

## 7. Interface d'administration MinIO absente (version Community)

**Problème.** Je cherchais à configurer les règles de cycle de vie depuis la
console web de MinIO, mais l'interface ne proposait que l'explorateur
d'objets, sans section Lifecycle. Ma version de MinIO Community n'expose pas
l'administration complète depuis la console.

**Solution.** J'ai utilisé le client en ligne de commande mc (MinIO Client),
déjà présent dans le conteneur MinIO. Cela m'a permis de configurer les
règles ILM directement en commande, ce qui est aussi plus reproductible et
traçable qu'une manipulation à la souris.

## 8. Chiffrement SSE-S3 impossible sans gestionnaire de clés (KMS)

**Problème.** Le brief demande d'activer le chiffrement SSE-S3 sur les
buckets de production. En lançant la commande d'activation
(mc encrypt set sse-s3 local/raw), MinIO a renvoyé une erreur : "Server
side encryption specified but KMS is not configured". Le chiffrement au
repos a besoin d'un gestionnaire de clés (KMS) pour stocker la clé de
chiffrement, et mon MinIO local n'en avait aucun.

**Solution.** La documentation MinIO propose deux approches. La première,
lourde, consiste à déployer un service dédié appelé KES (Key Encryption
Service) avec des certificats TLS, adapté à la production distribuée. La
seconde, beaucoup plus simple et adaptée à un déploiement local sur un seul
nœud, consiste à utiliser le KMS interne de MinIO, activé par une seule
variable d'environnement : MINIO_KMS_SECRET_KEY.

J'ai retenu la seconde approche. J'ai généré une clé maîtresse aléatoire
avec openssl rand -base64 32, je l'ai stockée dans un fichier .env (non
versionné, pour ne pas exposer le secret sur Git), et je l'ai référencée
dans le docker-compose de MinIO via la variable MINIO_KMS_SECRET_KEY. Après
redémarrage de MinIO, le KMS interne était actif (vérifié avec
mc admin kms key status). La commande d'activation du chiffrement a alors
fonctionné, et un fichier de test déposé dans raw affichait bien
"Encryption: SSE-S3" dans ses métadonnées.

En production, la clé maîtresse serait gérée par un coffre-fort externe
(HashiCorp Vault, AWS KMS) via KES, plutôt que par le KMS interne.