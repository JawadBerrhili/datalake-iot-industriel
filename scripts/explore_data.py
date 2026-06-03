"""
Exploration des 5 CSV : volumétrie, colonnes, types, anomalies.
Objectif : confirmer la carte des schémas avant décision d'architecture (C18).
"""
from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")

FILES = [
    "LineA_Stable_10K.csv",
    "LineB_Flux.csv",
    "LineC_Turbulent.csv",
    "LineD_SpikeControl.csv",
    "LineE_SmoothRun.csv",
]


def explore(filename):
    """Lit un CSV et affiche ses caractéristiques principales."""
    path = DATA_DIR / filename
    df = pd.read_csv(path)

    print("=" * 60)
    print(f"FICHIER : {filename}")
    print("-" * 60)
    print(f"Lignes      : {len(df)}")
    print(f"Colonnes    : {list(df.columns)}")
    print("Types :")
    print(df.dtypes.to_string())
    print("Aperçu (3 premières lignes) :")
    print(df.head(3).to_string())

    # Anomalies : répartition du champ label (s'il existe)
    if "label" in df.columns:
        print("Répartition label :")
        print(df["label"].value_counts().to_string())

    # Valeurs manquantes par colonne
    manquants = df.isnull().sum()
    if manquants.sum() > 0:
        print("Valeurs manquantes :")
        print(manquants[manquants > 0].to_string())
    else:
        print("Valeurs manquantes : aucune")
    print()


def main():
    for filename in FILES:
        explore(filename)


if __name__ == "__main__":
    main()