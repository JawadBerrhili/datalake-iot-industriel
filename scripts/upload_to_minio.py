"""
Upload des 5 CSV vers le bucket raw de MinIO, avec partitionnement
line=/year=/month=, et verification d'integrite via l'ETag (MD5) renvoye
par MinIO.
"""
import hashlib
from pathlib import Path

import boto3

DATA_DIR = Path("data")

# Connexion a MinIO 
s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin",
)

BUCKET = "raw"

# Chaque fichier avec sa ligne de production et son mois
FILES = {
    "LineA_Stable_10K.csv":   {"line": "lineA", "year": "2025", "month": "05"},
    "LineB_Flux.csv":         {"line": "lineB", "year": "2025", "month": "04"},
    "LineC_Turbulent.csv":    {"line": "lineC", "year": "2025", "month": "03"},
    "LineD_SpikeControl.csv": {"line": "lineD", "year": "2025", "month": "02"},
    "LineE_SmoothRun.csv":    {"line": "lineE", "year": "2025", "month": "01"},
}


def md5_of_file(path):
    """Empreinte MD5 du fichier local."""
    return hashlib.md5(path.read_bytes()).hexdigest()


def build_key(filename, info):
    """Construit la cle (chemin dans le bucket) avec partitionnement."""
    return (
        f"production_lines/"
        f"line={info['line']}/"
        f"year={info['year']}/"
        f"month={info['month']}/"
        f"{filename}"
    )


def main():
    for filename, info in FILES.items():
        path = DATA_DIR / filename
        key = build_key(filename, info)

        print(f"Upload de {filename} -> {key}")
        s3.upload_file(str(path), BUCKET, key)

        # Verification d'integrite : on compare notre MD5 a MinIO
        local_md5 = md5_of_file(path)
        head = s3.head_object(Bucket=BUCKET, Key=key)
        remote_etag = head["ETag"].strip('"')

        if local_md5 == remote_etag:
            print(f"  OK     integrite verifiee ({local_md5})")
        else:
            print(f"  ERREUR local {local_md5} != distant {remote_etag}")
    print("Termine.")


if __name__ == "__main__":
    main()