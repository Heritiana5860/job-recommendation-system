from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_mail import Mail
from src.email_service import EmailService
from src.data_manager import DataManager
from src.embeddings_matcher import EmbeddingsMatcher
from src.scheduler import init_scheduler
import config
import logging

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Créer l'app Flask
app = Flask(__name__)
app.config.from_object(config)

# Initialiser les services
mail = Mail(app)
EmailService(app)

# Initialiser le scheduler (optionnel)
# init_scheduler(app)

# Routes
@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/profile')
def profile():
    """Page de création/édition de profil"""
    return render_template('profile.html')

@app.route('/recommendations')
def recommendations():
    """Page des recommandations"""
    # La page se charge même sans profil sauvegardé
    # Le JavaScript s'occupera de vérifier la session storage
    return render_template('recommendations.html')

@app.route('/api/test-recommendations', methods=['POST'])
def test_recommendations():
    """API pour tester les recommandations (sans email)"""
    
    try:
        # Charger les données
        dm = DataManager()
        dm.load_profiles(config.MADAGASCAR_PROFILES_FILE)
        dm.load_scraped_jobs(config.MADAGASCAR_JOBS_FILE)
        
        # Entraîner le matcher
        matcher = EmbeddingsMatcher(model_type="word2vec")
        matcher.train_model(dm.profiles, dm.jobs)
        
        # Récupérer les recommandations pour le premier profil
        profile = dm.profiles[0]
        recommendations = matcher.recommend(profile, dm.jobs)
        
        # IMPORTANT: Convertir les scores float32 en float Python
        for rec in recommendations:
            rec['score'] = float(rec['score'])  # Convertir numpy.float32 en float
        
        return jsonify({
            'success': True,
            'profile_name': profile['name'],
            'recommendations': recommendations,
            'total': len(recommendations)
        })
    
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/send-test-email', methods=['POST'])
def send_test_email():
    """API pour envoyer un email de test"""
    
    try:
        data = request.json
        profile_email = data.get('email')
        
        if not profile_email:
            return jsonify({'success': False, 'error': 'Email requis'}), 400
        
        # Charger les données
        dm = DataManager()
        dm.load_profiles(config.MADAGASCAR_PROFILES_FILE)
        dm.load_scraped_jobs(config.MADAGASCAR_JOBS_FILE)
        
        # Matcher pour le premier profil
        matcher = EmbeddingsMatcher(model_type="word2vec")
        matcher.train_model(dm.profiles, dm.jobs)
        
        profile = dm.profiles[0]
        recommendations = matcher.recommend(profile, dm.jobs)
        
        # Envoyer l'email
        success = EmailService.send_recommendations_email(
            profile['name'],
            profile_email,
            recommendations
        )
        
        return jsonify({
            'success': success,
            'message': 'Email envoyé avec succès!' if success else 'Erreur lors de l\'envoi'
        })
    
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """API pour récupérer les profils"""
    try:
        dm = DataManager()
        dm.load_profiles(config.MADAGASCAR_PROFILES_FILE)
        return jsonify({'success': True, 'profiles': dm.profiles})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)