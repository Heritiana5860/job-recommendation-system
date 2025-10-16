# Moteur de matching simple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config import MIN_MATCH_SCORE, TOP_N_RECOMMENDATIONS

class SimpleMatcher:
    """Moteur de matching basé sur TF-IDF et similarité cosinus"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='french',
            analyzer='word',
            ngram_range=(1, 2)
        )
        self.profile_vector = None
        self.jobs_vectors = None
    
    def prepare_text(self, profile, jobs):
        """Prépare les textes pour la vectorisation"""
        profile_text = self._extract_profile_text(profile)
        jobs_texts = [self._extract_job_text(job) for job in jobs]
        return profile_text, jobs_texts
    
    def _extract_profile_text(self, profile):
        """Extrait et combine les informations pertinentes du profil"""
        parts = [
            profile.get('keywords', ''),
            ' '.join(profile.get('skills', [])),
            profile.get('desired_location', ''),
            ' '.join(profile.get('job_types', []))
        ]
        return ' '.join(parts).lower()
    
    def _extract_job_text(self, job):
        """Extrait et combine les informations pertinentes de l'offre"""
        parts = [
            job.get('title', ''),
            job.get('description', ''),
            ' '.join(job.get('required_skills', [])),
            job.get('location', ''),
            job.get('job_type', '')
        ]
        return ' '.join(parts).lower()
    
    def calculate_similarity(self, profile, jobs):
        """Calcule la similarité entre un profil et une liste d'offres"""
        profile_text, jobs_texts = self.prepare_text(profile, jobs)
        
        # Vectorize tous les textes ensemble
        all_texts = [profile_text] + jobs_texts
        vectors = self.vectorizer.fit_transform(all_texts)
        
        # Calcul de la similarité cosinus
        profile_vector = vectors[0]
        jobs_vectors = vectors[1:]
        
        similarities = cosine_similarity(profile_vector, jobs_vectors)[0]
        return similarities
    
    def add_score_filtering(self, profile, job, base_score):
        """Ajoute des scores supplémentaires basés sur les critères"""
        score = base_score
        
        # Bonus si la localisation correspond
        if profile.get('desired_location', '').lower() == job.get('location', '').lower():
            score += 0.1
        
        # Bonus si le type de contrat correspond
        if job.get('job_type') in profile.get('job_types', []):
            score += 0.1
        
        # Bonus si le salaire correspond
        job_salary_min = job.get('salary_min', 0)
        job_salary_max = job.get('salary_max', 999999)
        profile_salary_min = profile.get('salary_min', 0)
        profile_salary_max = profile.get('salary_max', 999999)
        
        if job_salary_min <= profile_salary_max and job_salary_max >= profile_salary_min:
            score += 0.05
        
        return min(score, 1.0)  # Cap à 1.0
    
    def recommend(self, profile, jobs):
        """Recommande les meilleures offres pour un profil"""
        if not jobs:
            return []
        
        similarities = self.calculate_similarity(profile, jobs)
        
        # Ajouter les scores additionnels
        final_scores = []
        for i, base_score in enumerate(similarities):
            final_score = self.add_score_filtering(profile, jobs[i], base_score)
            final_scores.append(final_score)
        
        # Créer les recommandations
        recommendations = []
        for i, job in enumerate(jobs):
            recommendations.append({
                'job_id': job['id'],
                'job_title': job['title'],
                'company': job['company'],
                'location': job['location'],
                'salary_range': f"{job.get('salary_min', 0)} - {job.get('salary_max', 0)}",
                'score': final_scores[i],
                'url': job.get('url', '#')  # À ajouter plus tard
            })
        
        # Trier par score et retourner les TOP N
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        recommendations = [r for r in recommendations if r['score'] >= MIN_MATCH_SCORE]
        
        return recommendations[:TOP_N_RECOMMENDATIONS]