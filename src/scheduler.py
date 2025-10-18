from apscheduler.schedulers.background import BackgroundScheduler
from src.data_manager import DataManager
from src.embeddings_matcher import EmbeddingsMatcher
from src.email_service import EmailService
from config import MADAGASCAR_PROFILES_FILE, MADAGASCAR_JOBS_FILE, SCHEDULER_TIME
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def daily_job():
    """Tâche quotidienne : scraper, matcher, et envoyer les emails"""
    
    logger.info("Début de la tâche quotidienne...")
    
    try:
        # Charger les données
        dm = DataManager()
        dm.load_profiles(MADAGASCAR_PROFILES_FILE)
        dm.load_scraped_jobs(MADAGASCAR_JOBS_FILE)
        
        # Entraîner le matcher
        matcher = EmbeddingsMatcher(model_type="word2vec")
        matcher.train_model(dm.profiles, dm.jobs)
        
        # Générer les recommandations et envoyer les emails
        for profile in dm.profiles:
            recommendations = matcher.recommend(profile, dm.jobs)
            
            if recommendations:
                success = EmailService.send_recommendations_email(
                    profile['name'],
                    profile['email'],
                    recommendations
                )
                status = "✓" if success else "✗"
                logger.info(f"{status} Email envoyé à {profile['name']}")
            else:
                logger.warning(f"Aucune recommandation pour {profile['name']}")
        
        logger.info("Tâche quotidienne terminée")
        
    except Exception as e:
        logger.error(f"Erreur lors de la tâche quotidienne: {str(e)}")

def init_scheduler(app):
    """Initialise le scheduler"""
    
    scheduler.add_job(
        func=daily_job,
        trigger="cron",
        hour=int(SCHEDULER_TIME.split(':')[0]),
        minute=int(SCHEDULER_TIME.split(':')[1]),
        id='daily_recommendation_job',
        name='Daily Job Recommendation',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info(f"Scheduler démarré - Tâche quotidienne à {SCHEDULER_TIME}")