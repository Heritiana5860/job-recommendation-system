import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
MODELS_DIR = BASE_DIR / "models"

# Configuration des données
SAMPLE_PROFILES_FILE = DATA_DIR / "sample_profiles.json"
SAMPLE_JOBS_FILE = DATA_DIR / "sample_jobs.json"
SCRAPED_JOBS_FILE = DATA_DIR / "scraped_jobs.json"
MADAGASCAR_PROFILES_FILE = DATA_DIR / "madagascar_profiles.json"
MADAGASCAR_JOBS_FILE = DATA_DIR / "madagascar_jobs.json"

# Configuration du matching
MIN_MATCH_SCORE = 0.3
TOP_N_RECOMMENDATIONS = 5

# Configuration des embeddings
EMBEDDING_MODEL = "word2vec"
EMBEDDING_DIM = 300
MIN_WORD_FREQ = 2

# Configuration RapidAPI
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST', 'jsearch.p.rapidapi.com')

# Configuration Flask
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = True

# Configuration Email
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', True)
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@job-recommendation.com')

# Configuration Scheduler
SCHEDULER_ENABLED = True
SCHEDULER_TIME = "08:00"  # Heure quotidienne pour envoyer les emails (8h du matin)