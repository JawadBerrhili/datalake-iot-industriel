# Analyse des données sources

## 1. Pourquoi cette analyse

Avant de décider quoi que ce soit sur l'architecture, je regarde d'abord ce
que contiennent vraiment les fichiers. Ce document note ce que j'ai trouvé :
le contenu, le volume, et surtout les différences de structure entre les
cinq fichiers. C'est ça qui guide ensuite mes choix techniques.

## 2. D'où viennent les données

Les données viennent d'un jeu public publié sur Zenodo en avril 2025
("Synthetic Data from Industrial Sensor Monitoring", Institut Polytechnique
de Porto / INESC TEC).

Elles simulent les relevés de capteurs de cinq lignes de production :
température, pression, et pour certaines lignes le temps de fonctionnement.
Il y a aussi un champ label : 0 quand tout est normal, 1 quand il y a une
anomalie.

J'ai vérifié que les cinq fichiers étaient bien intègres en comparant leur
empreinte MD5 avec celle fournie par Zenodo (voir le script
scripts/download_data.py).

## 3. Volume et période

| Fichier               | Lignes | Période       |
|-----------------------|--------|---------------|
| LineA_Stable_10K.csv  | 10 000 | Mai 2025      |
| LineB_Flux.csv        | 5 000  | Avril 2025    |
| LineC_Turbulent.csv   | 5 000  | Mars 2025     |
| LineD_SpikeControl.csv| 5 000  | Février 2025  |
| LineE_SmoothRun.csv   | 5 000  | Janvier 2025  |

Chaque fichier couvre un mois différent, avec une mesure par minute. Le
volume est petit (moins de 1 Mo par fichier), donc je peux traiter les
données simplement en mémoire.

## 4. Structure des fichiers

Tous les fichiers ont une base commune : timestamp, température, pression et
label. Mais la structure exacte change d'un fichier à l'autre.

| Fichier | Colonne température | Colonne pression | elapsed_time |
|---------|---------------------|------------------|--------------|
| LineA   | Temperature         | pressure         | elapsed_time |
| LineB   | temperature         | pressure         | Elapsed_time |
| LineC   | Temperature         | pressure         | absent       |
| LineD   | temperature         | Pressure         | absent       |
| LineE   | Temperature         | pressure         | absent       |

## 5. Les différences que j'ai repérées

En comparant les colonnes, je vois trois différences :

1. La casse de la température : parfois "Temperature", parfois "temperature".

2. La casse de la pression : LineD écrit "Pressure" avec une majuscule, les
   autres écrivent "pressure".

3. Le champ elapsed_time : il n'est présent que dans LineA et LineB, et même
   là sa casse change ("elapsed_time" pour LineA, "Elapsed_time" pour LineB).
   Il est absent de LineC, LineD et LineE.

Tant que ce n'est pas corrigé, je ne peux pas traiter les cinq fichiers
ensemble. Je règlerai ça à l'étape de transformation (couche staging).

## 6. Les anomalies

| Fichier | Anomalies (label = 1) | Taux  |
|---------|-----------------------|-------|
| LineA   | 18                    | 0,18 %|
| LineB   | 50                    | 1,00 %|
| LineC   | 200                   | 4,00 %|
| LineD   | 15                    | 0,30 %|
| LineE   | 25                    | 0,50 %|

Les anomalies sont rares partout (entre 0,18 % et 4 %). Ce déséquilibre est
important à garder en tête pour le futur projet de maintenance prédictive :
un modèle qui dirait toujours "normal" aurait l'air bon mais ne servirait
à rien.

## 7. Ce qui ne collait pas avec la fiche Zenodo

En regardant les vraies données, je me suis aperçu que la fiche descriptive
de Zenodo se trompait sur trois points :

- Elle annonçait 0 % d'anomalie pour LineE, alors qu'il y en a 25.
- Elle annonçait environ 5 % pour LineD, alors qu'il y en a 0,3 %.
- Elle donnait une pression autour de 19-20 pour LineB, alors que les vraies
  valeurs sont autour de 119.

Du coup, je documenterai mes fiches à partir des vraies données, pas de la
description.

## 8. Ce que je décide pour la suite

- Harmoniser les noms de colonnes en staging, tout en minuscules :
  timestamp, temperature, pressure, elapsed_time, label.

- Pour LineC, LineD et LineE qui n'ont pas elapsed_time, créer la colonne
  avec une valeur vide, pour que les cinq fichiers aient le même schéma.

- Convertir le timestamp en vraie date (pour l'instant il est lu comme du
  texte).

- Partitionner par mois en extrayant le mois depuis le timestamp, parce que
  chaque fichier couvre un mois différent.