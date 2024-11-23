import os
import sys
from dotenv import load_dotenv

TEAM_API_URL = os.getenv('TEAM_API_URL')
MATCH_API_URL = os.getenv('MATCH_API_URL')
POOL_API_URL = os.getenv('POOL_API_URL')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # Par défaut : INFO
PYTHON_DATASOURCE_URL = os.getenv('PYTHON_DATASOURCE_URL')

# Debugging pour vérifier les valeurs chargées
if __name__ == "__main__":
    print("Variables d'environnement chargées :")
    for key in [
        "TEAM_API_URL",
        "MATCH_API_URL",
        "POOL_API_URL",
        "LOG_LEVEL",
        "PYTHON_DATASOURCE_URL",
    ]:
        print(f"{key}: {os.getenv(key)}")
