from flask_mail import Mail, Message
from config import MAIL_DEFAULT_SENDER
from datetime import datetime

mail = Mail()

class EmailService:
    """Service d'envoi d'emails avec recommandations"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            mail.init_app(app)
    
    @staticmethod
    def send_recommendations_email(profile_name, profile_email, recommendations):
        """Envoie les recommandations d'emploi par email"""
        
        if not recommendations:
            return False
        
        # Construire le contenu HTML
        html_body = EmailService._build_email_html(profile_name, recommendations)
        
        try:
            msg = Message(
                subject=f"Vos recommandations d'emploi - {datetime.now().strftime('%d/%m/%Y')}",
                recipients=[profile_email],
                html=html_body
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Erreur lors de l'envoi à {profile_email}: {str(e)}")
            return False
    
    @staticmethod
    def _build_email_html(profile_name, recommendations):
        """Construit le contenu HTML de l'email"""
        
        html = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 20px auto; background: white; padding: 20px; border-radius: 8px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                    .job-card {{ border: 1px solid #ddd; margin: 15px 0; padding: 15px; border-radius: 5px; }}
                    .job-title {{ font-size: 18px; font-weight: bold; color: #333; }}
                    .company {{ color: #666; font-size: 14px; }}
                    .match-score {{ background: #4CAF50; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }}
                    .cta {{ text-align: center; margin-top: 20px; }}
                    .cta-button {{ background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; }}
                    .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Bonjour {profile_name}!</h1>
                        <p>Voici vos recommandations d'emploi du jour</p>
                    </div>
                    
                    <p>Nous avons trouvé <strong>{len(recommendations)}</strong> offres correspondant à votre profil:</p>
        """
        
        for i, rec in enumerate(recommendations, 1):
            html += f"""
                    <div class="job-card">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <div class="job-title">{i}. {rec['job_title']}</div>
                                <div class="company">{rec['company']} - {rec['location']}</div>
                            </div>
                            <div class="match-score">{rec['score']:.1%}</div>
                        </div>
                        <p style="margin-top: 10px;">
                            <a href="{rec['url']}" target="_blank" style="color: #667eea; text-decoration: none;">Voir l'offre →</a>
                        </p>
                    </div>
            """
        
        html += f"""
                    <div class="cta">
                        <p>Connectez-vous pour gérer vos préférences</p>
                    </div>
                    
                    <div class="footer">
                        <p>Système de Recommandation d'Emploi | Envoyé le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
                        <p>Ne pas répondre à cet email automatique</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return html