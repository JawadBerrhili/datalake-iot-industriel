"""
DAG de transformation : lit les CSV depuis raw, harmonise les colonnes,
normalise le timestamp, et depose le resultat dans staging.
Applique les decisions de l'analyse du Jour 1.
"""
import io
from datetime import datetime

import boto3
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator

MINIO_ENDPOINT = "http://minio:9000"
MINIO_KEY = "minioadmin"
MINIO_SECRET = "minioadmin"
RAW_BUCKET = "raw"
STAGING_BUCKET = "staging"

# Chaque fichier avec sa ligne et son mois (memes infos que l'ingestion)
FILES = {
    "LineA_Stable_10K.csv":   {"line": "lineA", "year": "2025", "month": "05"},
    "LineB_Flux.csv":         {"line": "lineB", "year": "2025", "month": "04"},
    "LineC_Turbulent.csv":    {"line": "lineC", "year": "2025", "month": "03"},
    "LineD_SpikeControl.csv": {"line": "lineD", "year": "2025", "month": "02"},
    "LineE_SmoothRun.csv":    {"line": "lineE", "year": "2025", "month": "01"},
}

# Schema cible : l'ordre et les noms de colonnes qu'on veut en sortie
SCHEMA_CIBLE = ["timestamp", "temperature", "pressure", "elapsed_time", "label"]


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_KEY,
        aws_secret_access_key=MINIO_SECRET,
    )


def transform_file(filename, info):
    """Lit un CSV depuis raw, l'harmonise, et l'ecrit dans staging."""
    s3 = get_s3_client()

    raw_key = (
        f"production_lines/"
        f"line={info['line']}/year={info['year']}/month={info['month']}/"
        f"{filename}"
    )

    # 1. Lire le CSV depuis raw
    obj = s3.get_object(Bucket=RAW_BUCKET, Key=raw_key)
    df = pd.read_csv(obj["Body"])
    print(f"Lu depuis raw : {raw_key} ({len(df)} lignes)")
    print(f"  Colonnes d'origine : {list(df.columns)}")

    # 2. Harmoniser les noms de colonnes : tout en minuscules
    df.columns = [col.lower() for col in df.columns]

    # 3. Ajouter elapsed_time si absent (lignes C, D, E)
    if "elapsed_time" not in df.columns:
        df["elapsed_time"] = pd.NA
        print("  Colonne elapsed_time ajoutee (vide)")

    # 4. Normaliser le timestamp : texte -> vraie date
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # 5. Reordonner selon le schema cible (toutes les lignes identiques)
    df = df[SCHEMA_CIBLE]
    print(f"  Colonnes harmonisees : {list(df.columns)}")

    # 6. Ecrire le resultat dans staging (via un buffer, sans fichier temporaire)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    staging_key = (
        f"production_lines/"
        f"line={info['line']}/year={info['year']}/month={info['month']}/"
        f"{filename}"
    )
    s3.put_object(
        Bucket=STAGING_BUCKET,
        Key=staging_key,
        Body=buffer.getvalue(),
    )
    print(f"Ecrit dans staging : {staging_key}")


with DAG(
    dag_id="transformation_staging",
    description="Harmonisation des CSV de raw vers staging",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["datalake", "transformation"],
) as dag:

    for filename, info in FILES.items():
        PythonOperator(
            task_id=f"transform_{info['line']}",
            python_callable=transform_file,
            op_kwargs={"filename": filename, "info": info},
        )