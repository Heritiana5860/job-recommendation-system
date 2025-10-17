import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Chemins
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"

# Configuration des données
SAMPLE_PROFILES_FILE = DATA_DIR / "sample_profiles.json"
SAMPLE_JOBS_FILE = DATA_DIR / "sample_jobs.json"
SCRAPED_JOBS_FILE = DATA_DIR / "scraped_jobs.json"

# Configuration du matching
MIN_MATCH_SCORE = 0.05  # Score minimum pour une recommendation
TOP_N_RECOMMENDATIONS = 5  # Nombre d'offres à recommander par jour

# Configuration RapidAPI / JSearch
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST', 'jsearch.p.rapidapi.com')

# Configuration de recherche
SEARCH_QUERIES = [
    {"query": "Python developer", "location": "Madagascar"},
    {"query": "Data scientist", "location": "France"},
    {"query": "Frontend developer", "location": "Paris"},
    {"query": "Machine learning engineer", "location": "USA"}
]

# Logging
DEBUG = True