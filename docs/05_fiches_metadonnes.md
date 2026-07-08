# Fiches de métadonnées - Lignes de production

Ces fiches documentent les 5 jeux de données du data lake. Elles serviront
de référence pour le catalogue OpenMetadata (une entrée par ligne).

## Informations communes aux 5 lignes

- Source : Synthetic Data from Industrial Sensor Monitoring - Institut
  Polytechnique de Porto / INESC TEC, publié sur Zenodo en avril 2025.
- Fréquence de collecte : une mesure par minute.
- Nature : données synthétiques (générées) simulant des capteurs industriels.
- Emplacement dans le data lake : bucket staging, données harmonisées.

## Colonnes (schéma harmonisé, commun aux 5 lignes)

- timestamp : horodatage de la mesure (une par minute).
- temperature : température relevée par le capteur. Valeurs observées
  autour de 180 à 200 selon la ligne (données synthétiques, unité non
  précisée par la source).
- pressure : pression relevée. Valeurs observées autour de 99 à 160
  selon la ligne.
- elapsed_time : temps de fonctionnement. Présent sur les lignes A et B,
  vide sur les lignes C, D et E (colonne ajoutée lors de l'harmonisation
  pour uniformiser le schéma).
- label : indicateur d'anomalie. 0 = fonctionnement nominal,
  1 = anomalie détectée.

---

## Ligne A — Stable

- Description : ligne de production au comportement stable.
- Propriétaire : Responsable maintenance Ligne A (ex. Julien Thibaut).
- Volume : 10 000 mesures.
- Période couverte : mai 2025.
- Taux d'anomalie : 0,18 % (18 anomalies).
- elapsed_time : présent.

## Ligne B — Flux moyen

- Description : ligne de production à flux moyen.
- Propriétaire : Responsable maintenance Ligne B (ex. Sophie Renaud).
- Volume : 5 000 mesures.
- Période couverte : avril 2025.
- Taux d'anomalie : 1,00 % (50 anomalies).
- elapsed_time : présent.

## Ligne C — Turbulente

- Description : ligne de production au comportement turbulent, taux
  d'anomalie le plus élevé des cinq lignes.
- Propriétaire : Responsable maintenance Ligne C (ex. Marc Olivier).
- Volume : 5 000 mesures.
- Période couverte : mars 2025.
- Taux d'anomalie : 4,00 % (200 anomalies).
- elapsed_time : absent (ajouté vide à l'harmonisation).

## Ligne D — Avec pics

- Description : ligne de production présentant des pics de mesures.
- Propriétaire : Responsable maintenance Ligne D (ex. Nadia Cherif).
- Volume : 5 000 mesures.
- Période couverte : février 2025.
- Taux d'anomalie : 0,30 % (15 anomalies).
- elapsed_time : absent (ajouté vide à l'harmonisation).

## Ligne E — Variable

- Description : ligne de production au comportement variable.
- Propriétaire : Responsable maintenance Ligne E (ex. Thomas Girard).
- Volume : 5 000 mesures.
- Période couverte : janvier 2025.
- Taux d'anomalie : 0,50 % (25 anomalies).
- elapsed_time : absent (ajouté vide à l'harmonisation).