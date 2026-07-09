# Règles de cycle de vie des données (ILM)

Ce document décrit les règles de cycle de vie appliquées aux données du
data lake, conformément au brief (archivage après 180 jours, suppression
après 2 ans). Les règles sont appliquées sur le bucket raw, qui contient
les données brutes conservées le plus longtemps.

## Règle 1 — Suppression automatique après 2 ans (active)

Les objets âgés de plus de 730 jours (2 ans) sont automatiquement supprimés.

- Statut : configurée et active dans MinIO.
- Type : expiration.
- Mise en œuvre : règle ILM native de MinIO, créée avec le client mc :
  mc ilm rule add local/raw --expire-days 730
- Objectif : éviter la conservation indéfinie de données anciennes et
  maîtriser le volume de stockage.

## Règle 2 — Archivage après 180 jours (documentée, applicable en production)

Les objets âgés de plus de 180 jours sont destinés à être déplacés vers un
stockage d'archivage (tier froid), moins coûteux et moins sollicité.

- Statut : documentée, non active en environnement local.
- Type : transition vers un tier de stockage.
- Raison : dans MinIO, une transition nécessite un tier de destination
  distinct. En local, sur un seul nœud, la configuration d'un tier
  auto-référencé n'a pas abouti (voir docs/06_problemes_rencontres.md,
  point 6). En production, avec un stockage d'archivage distant disponible,
  cette règle se configure ainsi :
  mc ilm tier add minio <alias> ARCHIVE_TIER --endpoint <url> --bucket archive
  mc ilm rule add local/raw --transition-days 180 --storage-class ARCHIVE_TIER
- Objectif : réduire les coûts de stockage en déplaçant les données peu
  consultées vers un stockage moins cher, tout en les conservant.

## Synthèse

| Règle       | Délai     | Action            | Statut                        |
|-------------|-----------|-------------------|-------------------------------|
| Expiration  | 730 jours | Suppression       | Active                        |
| Transition  | 180 jours | Archivage (tier)  | Documentée (prod uniquement)  |