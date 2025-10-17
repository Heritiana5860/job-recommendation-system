import requests
import json
from datetime import datetime
from config import RAPIDAPI_KEY, RAPIDAPI_HOST, SCRAPED_JOBS_FILE
import time

class JSearchScraper:
    """Scraper pour récupérer les offres d'emploi via JSearch API"""
    
    def __init__(self):
        self.api_key = RAPIDAPI_KEY
        self.api_host = RAPIDAPI_HOST
        self.base_url = "https://jsearch.p.rapidapi.com/search"
        self.jobs = []
        self.errors = []
    
    def _validate_api_key(self):
        """Vérifie que la clé API est configurée"""
        if not self.api_key:
            raise ValueError(
                "❌ RAPIDAPI_KEY non configurée. "
                "Créez un fichier .env avec votre clé API"
            )
    
    def search_jobs(self, query, location, pages=1):
        """
        Récupère les offres d'emploi via JSearch
        
        Args:
            query (str): Poste recherché (ex: "Python developer")
            location (str): Localisation (ex: "France")
            pages (int): Nombre de pages à récupérer (défaut: 1)
        """
        self._validate_api_key()
        
        headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': self.api_host
        }
        
        print(f"\n🔍 Recherche: {query} - {location}")
        
        for page in range(1, pages + 1):
            querystring = {
                "query": query,
                "location": location,
                "page": page,
                "num_pages": 1
            }
            
            try:
                response = requests.get(
                    self.base_url,
                    headers=headers,
                    params=querystring,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    jobs_data = data.get('data', [])
                    
                    if not jobs_data:
                        print(f"   Page {page}: Aucune offre trouvée")
                        break
                    
                    print(f"   Page {page}: {len(jobs_data)} offres trouvées")
                    self._parse_jobs(jobs_data, query)
                    
                    # Attendre un peu entre les requêtes pour respecter les limites
                    if page < pages:
                        time.sleep(1)
                
                elif response.status_code == 429:
                    print(f"   ⚠️ Limite d'API atteinte. Attendez quelques minutes.")
                    break
                else:
                    error = f"Erreur {response.status_code} pour {query}"
                    print(f"   ❌ {error}")
                    self.errors.append(error)
                    
            except requests.exceptions.Timeout:
                error = f"Timeout lors de la recherche: {query}"
                print(f"   ❌ {error}")
                self.errors.append(error)
            except Exception as e:
                error = f"Erreur lors du scraping: {str(e)}"
                print(f"   ❌ {error}")
                self.errors.append(error)
    
    def _parse_jobs(self, jobs_data, search_query):
        """Parse les données brutes en format standardisé"""
        
        for job in jobs_data:
            try:
                parsed_job = {
                    'id': job.get('job_id', ''),
                    'title': job.get('job_title', 'N/A'),
                    'company': job.get('employer_name', 'N/A'),
                    'location': job.get('job_location', 'N/A'),
                    'description': job.get('job_description', ''),
                    'job_type': job.get('job_employment_type', 'CDI'),
                    'required_skills': self._extract_skills(job.get('job_description', '')),
                    'salary_min': job.get('job_salary_min', None),
                    'salary_max': job.get('job_salary_max', None),
                    'posted_date': job.get('job_posted_at_datetime_utc', datetime.now().isoformat()),
                    'url': job.get('job_apply_link', '#'),
                    'search_query': search_query,
                    'source': 'JSearch API'
                }
                self.jobs.append(parsed_job)
            except Exception as e:
                print(f"   ⚠️ Erreur parsing job: {str(e)}")
    
    def _extract_skills(self, description):
        """Extrait les compétences de la description"""
        # Liste commune de compétences techniques
        tech_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust',
            'React', 'Vue', 'Angular', 'Node.js', 'Django', 'Flask', 'Spring',
            'Machine Learning', 'Deep Learning', 'AI', 'Data Analysis', 'SQL',
            'Git', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP',
            'HTML', 'CSS', 'REST API', 'GraphQL', 'MongoDB', 'PostgreSQL'
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in tech_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills if found_skills else []
    
    def get_jobs(self):
        """Retourne tous les jobs scraped"""
        return self.jobs
    
    def get_unique_jobs(self):
        """Retourne les jobs sans doublons (basé sur job_id)"""
        seen = set()
        unique_jobs = []
        
        for job in self.jobs:
            job_id = job.get('id')
            if job_id not in seen:
                seen.add(job_id)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def save_to_json(self, filepath=SCRAPED_JOBS_FILE):
        """Sauvegarde les jobs en JSON"""
        unique_jobs = self.get_unique_jobs()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'jobs': unique_jobs,
                'total': len(unique_jobs),
                'scraped_at': datetime.now().isoformat(),
                'errors': self.errors
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ {len(unique_jobs)} offres sauvegardées dans {filepath}")
        
        if self.errors:
            print(f"⚠️  {len(self.errors)} erreurs rencontrées")
    
    def get_stats(self):
        """Affiche les statistiques du scraping"""
        unique_jobs = self.get_unique_jobs()
        
        print("\n" + "="*60)
        print("STATISTIQUES DU SCRAPING")
        print("="*60)
        print(f"Total offres scrappées: {len(unique_jobs)}")
        print(f"Erreurs: {len(self.errors)}")
        
        # Offres par entreprise
        companies = {}
        for job in unique_jobs:
            company = job.get('company', 'Unknown')
            companies[company] = companies.get(company, 0) + 1
        
        print(f"\nTop 5 entreprises:")
        for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {company}: {count} offres")
        
        # Localisation
        locations = {}
        for job in unique_jobs:
            location = job.get('location', 'Unknown')
            locations[location] = locations.get(location, 0) + 1
        
        print(f"\nTop 5 localisations:")
        for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {location}: {count} offres")