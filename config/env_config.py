import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis un fichier .env
load_dotenv()

# Variables d'environnement
TEAM_API_URL = os.getenv('TEAM_API_URL', 'http://localhost:8082/api/teams')
MATCH_API_URL = os.getenv('MATCH_API_URL', 'http://localhost:8083/api/matches')
POOL_API_URL = os.getenv('POOL_API_URL', 'http://localhost:8081/api/pools')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://blockout_scraper:blockout_scraper@localhost:5435/blockout_scraper')
