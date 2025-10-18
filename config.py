import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Chemins
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
MODELS_DIR = BASE_DIR / "models"

# Créer le dossier models s'il n'existe pas
MODELS_DIR.mkdir(exist_ok=True)

# Configuration des données
SAMPLE_PROFILES_FILE = DATA_DIR / "sample_profiles.json"
SAMPLE_JOBS_FILE = DATA_DIR / "sample_jobs.json"
SCRAPED_JOBS_FILE = DATA_DIR / "scraped_jobs.json"

# Configuration du matching
MIN_MATCH_SCORE = 0.3 # Score minimum pour une recommendation
TOP_N_RECOMMENDATIONS = 5  # Nombre d'offres à recommander par jour

# Configuration des embeddings
EMBEDDING_MODEL = "word2vec"  # Options: "word2vec", "fasttext"
EMBEDDING_DIM = 300
MIN_WORD_FREQ = 2

# Configuration RapidAPI / JSearch
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST', 'jsearch.p.rapidapi.com')

# Configuration de recherche
SEARCH_QUERIES = [
    {"query": "Python developer", "location": "Antananarivo, Madagascar"},
    {"query": "Python developer", "location": "Fianarantsoa, Madagascar"},
    {"query": "Python developer", "location": "Toliara, Madagascar"},
    {"query": "Data scientist", "location": "Antananarivo, Madagascar"},
    {"query": "Data scientist", "location": "Fianarantsoa, Madagascar"},
    {"query": "Machine learning", "location": "Madagascar"},
]

# Logging
DEBUG = True