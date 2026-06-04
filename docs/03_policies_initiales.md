# Policies d'accès initiales

Tous les buckets sont configurés en accès **Private** : aucune donnée
n'est accessible publiquement ou anonymement. L'accès passe uniquement
par des comptes authentifiés.

Principe d'accès prévu par bucket (détaillé au Jour 6 avec les comptes de service) :

- raw      : écriture par les pipelines d'ingestion, lecture par les data engineers
- staging  : lecture / écriture par les data engineers
- curated  : lecture seule pour les analystes, écriture par les pipelines
- archive  : lecture restreinte, géré par la règle de cycle de vie

Le détail des droits par rôle (data-analyst, data-engineer, admin) sera
mis en place lors de l'étape de gouvernance.