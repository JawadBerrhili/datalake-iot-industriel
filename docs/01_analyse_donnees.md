# Analyse des données sources

## 1. Objectif

Ce document présente l'analyse des cinq fichiers de données avant toute
décision technique. Il identifie le contenu, le volume et surtout les
différences de structure entre les fichiers. Ces constats servent de base
aux choix d'architecture du data lake.

## 2. Source des données

Les données proviennent du jeu de données public "Synthetic Data from
Industrial Sensor Monitoring" (Institut Polytechnique de Porto / INESC TEC),
publié sur Zenodo en avril 2025.

Elles simulent les relevés de capteurs de cinq lignes de production
industrielles : température, pression, et pour certaines lignes le temps de
fonctionnement. Chaque ligne possède aussi un indicateur d'anomalie.

L'intégrité des cinq fichiers a été vérifiée à l'aide des empreintes MD5
officielles publiées par Zenodo (voir le script `scripts/download_data.py`).

## 3. Volumétrie et période

| Fichier               | Lignes | Période       |
|-----------------------|--------|---------------|
| LineA_Stable_10K.csv  | 10 000 | Mai 2025      |
| LineB_Flux.csv        | 5 000  | Avril 2025    |
| LineC_Turbulent.csv   | 5 000  | Mars 2025     |
| LineD_SpikeControl.csv| 5 000  | Février 2025  |
| LineE_SmoothRun.csv   | 5 000  | Janvier 2025  |

Chaque fichier couvre un mois différent. Les mesures sont relevées chaque
minute.

## 4. Structure de chaque fichier

Les cinq fichiers partagent un socle commun : un horodatage (timestamp),
une température, une pression, et un indicateur d'anomalie (label).
Le champ label vaut 0 pour un fonctionnement normal et 1 pour une anomalie.

Cependant, la structure exacte diffère d'un fichier à l'autre.

| Fichier | Colonne température | Colonne pression | elapsed_time |
|---------|---------------------|------------------|--------------|
| LineA   | Temperature         | pressure         | elapsed_time |
| LineB   | temperature         | pressure         | Elapsed_time |
| LineC   | Temperature         | pressure         | absent       |
| LineD   | temperature         | Pressure         | absent       |
| LineE   | Temperature         | pressure         | absent       |

## 5. Différences de structure identifiées

Trois différences ont été constatées entre les fichiers :

1. **La casse de la colonne température.** Certains fichiers écrivent
   "Temperature" avec une majuscule, d'autres "temperature" en minuscule.

2. **La casse de la colonne pression.** Le fichier LineD écrit "Pressure"
   avec une majuscule, tous les autres écrivent "pressure" en minuscule.

3. **Le champ elapsed_time.** Il est présent uniquement dans LineA et LineB,
   et absent de LineC, LineD et LineE. De plus, sa casse diffère entre les
   deux fichiers qui le contiennent : "elapsed_time" pour LineA,
   "Elapsed_time" pour LineB.

Cela empêche d'exploiter les cinq fichiers ensemble en l'état.
Elle devra être corrigée lors de l'étape de transformation (couche staging).

## 6. Répartition des anomalies

| Fichier | Anomalies (label = 1) | Taux  |
|---------|-----------------------|-------|
| LineA   | 18                    | 0,18 %|
| LineB   | 50                    | 1,00 %|
| LineC   | 200                   | 4,00 %|
| LineD   | 15                    | 0,30 %|
| LineE   | 25                    | 0,50 %|

Les anomalies sont rares dans tous les fichiers (entre 0,18 % et 4 %).
Ce fort déséquilibre devra être pris en compte par le futur projet de
maintenance prédictive.

## 7. Écarts avec la fiche descriptive de la source

L'analyse des données réelles a révélé trois écarts avec la fiche
descriptive publiée sur Zenodo :

- La fiche annonçait 0 % d'anomalie pour LineE ; la donnée en contient 25.
- La fiche annonçait environ 5 % d'anomalie pour LineD ; la donnée en
  contient 0,3 %.
- La fiche indiquait une plage de pression d'environ 19-20 pour LineB ;
  les valeurs réelles sont d'environ 119.

Ces écarts confirment qu'il faut documenter le data lake à partir des
données réelles, et non de leur description.

## 8. Conclusions et décisions techniques

Les constats ci-dessus conduisent aux décisions suivantes :

- **Harmonisation des noms de colonnes** en couche staging, vers une
  convention unique en minuscules : timestamp, temperature, pressure,
  elapsed_time, label.

- **Gestion du champ manquant** : pour LineC, LineD et LineE, la colonne
  elapsed_time sera créée avec une valeur vide, afin que les cinq fichiers
  partagent le même schéma.

- **Normalisation de l'horodatage** : le champ timestamp est actuellement
  lu comme du texte. Il sera converti en type date et heure en staging.

- **Partitionnement par mois** : le mois sera extrait de l'horodatage
  plutôt que codé en dur, car chaque fichier couvre un mois distinct.