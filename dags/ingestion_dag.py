"""
DAG d'ingestion : depose chaque CSV dans le bucket raw de MinIO
avec partitionnement line=/year=/month=.
LineA est traitee par chunks pour simuler un flux reel.
"""
from datetime import datetime

import boto3
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator

# Connexion a MinIO : ici on utilise le nom du service, pas localhost, car c'est Airflow qui se connecte a MinIO via le reseau Docker compose
MINIO_ENDPOINT = "http://minio:9000"
MINIO_KEY = "minioadmin"
MINIO_SECRET = "minioadmin"
BUCKET = "raw"

DATA_DIR = "/opt/airflow/data"

# Chaque fichier avec sa ligne et son mois (etablis a l'analyse du Jour 1)
FILES = {
    "LineA_Stable_10K.csv":   {"line": "lineA", "year": "2025", "month": "05"},
    "LineB_Flux.csv":         {"line": "lineB", "year": "2025", "month": "04"},
    "LineC_Turbulent.csv":    {"line": "lineC", "year": "2025", "month": "03"},
    "LineD_SpikeControl.csv": {"line": "lineD", "year": "2025", "month": "02"},
    "LineE_SmoothRun.csv":    {"line": "lineE", "year": "2025", "month": "01"},
}


def get_s3_client():
    """Cree un client boto3 connecte a MinIO."""
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_KEY,
        aws_secret_access_key=MINIO_SECRET,
    )


def ingest_file(filename, info):
    """Depose un CSV dans raw/ avec partitionnement. LineA est lue par chunks."""
    s3 = get_s3_client()
    key = (
        f"production_lines/"
        f"line={info['line']}/year={info['year']}/month={info['month']}/"
        f"{filename}"
    )
    local_path = f"{DATA_DIR}/{filename}"

    # LineA (10 000 lignes) : on simule un flux en lisant par morceaux de 1000 lignes
    if info["line"] == "lineA":
        chunks = pd.read_csv(local_path, chunksize=1000)
        nb = 0
        for i, chunk in enumerate(chunks):
            nb += len(chunk)
            print(f"  LineA chunk {i} : {len(chunk)} lignes (cumul {nb})")
        print(f"LineA lue en {i + 1} chunks, total {nb} lignes")

    # Depot du fichier dans MinIO
    s3.upload_file(local_path, BUCKET, key)
    print(f"Depose : {key}")


with DAG(
    dag_id="ingestion_raw",
    description="Ingestion des CSV vers le bucket raw avec partitionnement",
    start_date=datetime(2025, 1, 1),
    schedule=None,          # declenche manuellement, pas en auto
    catchup=False,
    tags=["datalake", "ingestion"],
) as dag:

    # Une tache par fichier
    for filename, info in FILES.items():
        PythonOperator(
            task_id=f"ingest_{info['line']}",
            python_callable=ingest_file,
            op_kwargs={"filename": filename, "info": info},
        )