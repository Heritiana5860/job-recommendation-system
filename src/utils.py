# Utilitaires

import json
from datetime import datetime

def print_recommendations(profile_name, recommendations):
    """Affiche les recommandations de manière lisible"""
    print(f"\n{'='*60}")
    print(f"Recommandations pour {profile_name}")
    print(f"{'='*60}")
    
    if not recommendations:
        print("Aucune recommandation trouvée.")
        return
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['job_title']} - {rec['company']}")
        print(f"   Location: {rec['location']}")
        print(f"   Salary: {rec['salary_range']}")
        print(f"   Score de match: {rec['score']:.2%}")
        print(f"   URL: {rec['url']}")

def export_recommendations_to_json(all_recommendations, filename='recommendations_export.json'):
    """Exporte les recommandations en JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_recommendations, f, ensure_ascii=False, indent=2)
    print(f"✓ Recommandations exportées vers {filename}")