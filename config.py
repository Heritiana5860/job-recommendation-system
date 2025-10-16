import os
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"

# Configuration des données
SAMPLE_PROFILES_FILE = DATA_DIR / "sample_profiles.json"
SAMPLE_JOBS_FILE = DATA_DIR / "sample_jobs.json"

# Configuration du matching
MIN_MATCH_SCORE = 0.3  # Score minimum pour une recommendation
TOP_N_RECOMMENDATIONS = 5  # Nombre d'offres à recommander par jour

# Logging
DEBUG = True