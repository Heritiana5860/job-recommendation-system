# Gestion des données

import json
import pandas as pd
from pathlib import Path
from config import SAMPLE_PROFILES_FILE, SAMPLE_JOBS_FILE

class DataManager:
    """Gestionnaire de données pour profils et offres d'emploi"""
    
    def __init__(self):
        self.profiles = []
        self.jobs = []
    
    def load_profiles(self, file_path=SAMPLE_PROFILES_FILE):
        """Charge les profils utilisateur depuis un JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.profiles = data.get('profiles', [])
            print(f"✓ {len(self.profiles)} profils chargés")
            return self.profiles
        except FileNotFoundError:
            print(f"✗ Fichier non trouvé: {file_path}")
            return []
    
    def load_jobs(self, file_path=SAMPLE_JOBS_FILE):
        """Charge les offres d'emploi depuis un JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.jobs = data.get('jobs', [])
            print(f"✓ {len(self.jobs)} offres chargées")
            return self.jobs
        except FileNotFoundError:
            print(f"✗ Fichier non trouvé: {file_path}")
            return []
    
    def get_profile(self, profile_id):
        """Récupère un profil par ID"""
        return next((p for p in self.profiles if p['id'] == profile_id), None)
    
    def get_all_profiles_df(self):
        """Retourne tous les profils sous forme de DataFrame pandas"""
        return pd.DataFrame(self.profiles)
    
    def get_all_jobs_df(self):
        """Retourne toutes les offres sous forme de DataFrame pandas"""
        return pd.DataFrame(self.jobs)
    
    def save_profiles(self, file_path=SAMPLE_PROFILES_FILE):
        """Sauvegarde les profils en JSON"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({'profiles': self.profiles}, f, ensure_ascii=False, indent=2)
        print(f"✓ Profils sauvegardés")
    
    def save_jobs(self, file_path=SAMPLE_JOBS_FILE):
        """Sauvegarde les offres en JSON"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({'jobs': self.jobs}, f, ensure_ascii=False, indent=2)
        print(f"✓ Offres sauvegardées")