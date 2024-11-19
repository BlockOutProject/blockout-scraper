import logging
from config.env_config import LOG_LEVEL

# Récupérer le niveau de log depuis une variable d'environnement
log_level = getattr(logging, LOG_LEVEL, logging.INFO)  # Convertir en niveau numérique

# Configurer le logger de base
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)