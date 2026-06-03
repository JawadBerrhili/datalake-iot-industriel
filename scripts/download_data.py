"""
Téléchargement des 5 CSV depuis Zenodo + vérification d'intégrité MD5.
Source : https://zenodo.org/records/15277168
"""
import hashlib
from pathlib import Path

import requests

# Dossier de destination (créé s'il n'existe pas déjà)
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# URL de base des fichiers sur Zenodo
BASE_URL = "https://zenodo.org/records/15277168/files"

# Chaque fichier associé à son empreinte MD5 officielle (publiée par Zenodo)
FILES = {
    "LineA_Stable_10K.csv":   "664d60672e369352f5235c9376f4c947",
    "LineB_Flux.csv":         "cb1ef784bb5a99098ec43a763b9a1e67",
    "LineC_Turbulent.csv":    "cb408152cc4729b4384d5b1c9667bd97",
    "LineD_SpikeControl.csv": "1adc02fec2893d071ecba27d85e1754b",
    "LineE_SmoothRun.csv":    "c29839ffd6ea599dc600b3c353b996ac",
}


def md5_of_file(path):
    """Calcule l'empreinte MD5 d'un fichier (lu en une fois, fichiers petits)."""
    contenu = path.read_bytes()          # lit tout le fichier en binaire
    return hashlib.md5(contenu).hexdigest()


def download(filename):
    """Télécharge un fichier depuis Zenodo vers le dossier data/."""
    url = f"{BASE_URL}/{filename}?download=1"
    destination = DATA_DIR / filename
    print(f"Téléchargement de {filename} ...")
    response = requests.get(url)
    response.raise_for_status()          # stoppe net si erreur HTTP (404, 500...)
    destination.write_bytes(response.content)
    return destination


def main():
    for filename, expected_md5 in FILES.items():
        path = download(filename)
        actual_md5 = md5_of_file(path)
        if actual_md5 == expected_md5:
            print(f"  OK     {filename} — intégrité vérifiée")
        else:
            print(f"  ERREUR {filename} — attendu {expected_md5}, obtenu {actual_md5}")
    print("Terminé.")


if __name__ == "__main__":
    main()