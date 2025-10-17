from gensim.models import Word2Vec, FastText
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
from config import EMBEDDING_MODEL, EMBEDDING_DIM, MIN_WORD_FREQ, MIN_MATCH_SCORE, TOP_N_RECOMMENDATIONS
import os

# Télécharger les ressources NLTK si nécessaire
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class EmbeddingsMatcher:
    """Moteur de matching utilisant Word2Vec ou FastText embeddings"""
    
    def __init__(self, model_type="word2vec"):
        self.model_type = model_type
        self.model = None
        self.french_stops = set(stopwords.words('french'))
        self.english_stops = set(stopwords.words('english'))
    
    def _preprocess_text(self, text):
        """Nettoie et tokenise le texte"""
        # Convertir en minuscules
        text = text.lower()
        
        # Tokenizer
        tokens = word_tokenize(text)
        
        # Supprimer les stop words et les caractères spéciaux
        tokens = [
            token for token in tokens 
            if token.isalnum() and token not in self.french_stops and token not in self.english_stops
        ]
        
        return tokens
    
    def train_model(self, profiles, jobs):
        """Entraîne le modèle d'embeddings sur les profils et offres"""
        print(f"📚 Entraînement du modèle {self.model_type.upper()}...")
        
        # Préparer tous les textes
        all_texts = []
        
        # Ajouter les textes des profils
        for profile in profiles:
            text = self._extract_profile_text(profile)
            tokens = self._preprocess_text(text)
            if tokens:
                all_texts.append(tokens)
        
        # Ajouter les textes des offres
        for job in jobs:
            text = self._extract_job_text(job)
            tokens = self._preprocess_text(text)
            if tokens:
                all_texts.append(tokens)
        
        print(f"   Documents traités: {len(all_texts)}")
        
        # Entraîner le modèle
        if self.model_type == "word2vec":
            self.model = Word2Vec(
                sentences=all_texts,
                vector_size=EMBEDDING_DIM,
                window=5,
                min_count=MIN_WORD_FREQ,
                workers=4,
                sg=1  # Skip-gram
            )
        elif self.model_type == "fasttext":
            self.model = FastText(
                sentences=all_texts,
                vector_size=EMBEDDING_DIM,
                window=5,
                min_count=MIN_WORD_FREQ,
                workers=4
            )
        
        print(f"   Modèle entraîné! Vocabulaire: {len(self.model.wv)} mots")
        return self.model
    
    def _extract_profile_text(self, profile):
        """Extrait le texte pertinent du profil"""
        parts = [
            profile.get('keywords', ''),
            ' '.join(profile.get('skills', [])),
            profile.get('desired_location', ''),
            ' '.join(profile.get('job_types', []))
        ]
        return ' '.join(parts)
    
    def _extract_job_text(self, job):
        """Extrait le texte pertinent de l'offre"""
        parts = [
            job.get('title', ''),
            job.get('description', ''),
            ' '.join(job.get('required_skills', [])),
            job.get('location', ''),
            job.get('job_type', '')
        ]
        return ' '.join(parts)
    
    def _get_text_embedding(self, text):
        """Obtient l'embedding moyen d'un texte"""
        if not self.model:
            raise ValueError("Le modèle n'a pas été entraîné. Appelez train_model() d'abord.")
        
        tokens = self._preprocess_text(text)
        
        if not tokens:
            # Retourner un vecteur zéro si pas de tokens
            return np.zeros(EMBEDDING_DIM)
        
        # Moyenne des embeddings des mots présents
        embeddings = []
        for token in tokens:
            if token in self.model.wv:
                embeddings.append(self.model.wv[token])
        
        if not embeddings:
            return np.zeros(EMBEDDING_DIM)
        
        return np.mean(embeddings, axis=0)
    
    def calculate_similarity(self, profile, jobs):
        """Calcule la similarité entre un profil et des offres"""
        profile_text = self._extract_profile_text(profile)
        profile_embedding = self._get_text_embedding(profile_text)
        
        similarities = []
        for job in jobs:
            job_text = self._extract_job_text(job)
            job_embedding = self._get_text_embedding(job_text)
            
            # Calcul de similarité cosinus
            similarity = cosine_similarity(
                [profile_embedding],
                [job_embedding]
            )[0][0]
            
            similarities.append(similarity)
        
        return np.array(similarities)
    
    def add_score_filtering(self, profile, job, base_score):
        """Ajoute des bonus basés sur les critères"""
        score = base_score
        
        # Bonus localisation
        if profile.get('desired_location', '').lower() == job.get('location', '').lower():
            score += 0.15
        
        # Bonus type de contrat
        if job.get('job_type') in profile.get('job_types', []):
            score += 0.10
        
        # Bonus salaire (gérer les None)
        job_salary_min = job.get('salary_min') or 0
        job_salary_max = job.get('salary_max') or 999999
        profile_salary_min = profile.get('salary_min', 0)
        profile_salary_max = profile.get('salary_max', 999999)
        
        if job_salary_min and job_salary_max:
            if job_salary_min <= profile_salary_max and job_salary_max >= profile_salary_min:
                score += 0.10
        
        return min(score, 1.0)
    
    def recommend(self, profile, jobs):
        """Recommande les meilleures offres pour un profil"""
        if not jobs or not self.model:
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
                'salary_range': f"{job.get('salary_min', 'N/A')} - {job.get('salary_max', 'N/A')}",
                'score': final_scores[i],
                'url': job.get('url', '#')
            })
        
        # Trier et filtrer
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        recommendations = [r for r in recommendations if r['score'] >= MIN_MATCH_SCORE]
        
        return recommendations[:TOP_N_RECOMMENDATIONS]