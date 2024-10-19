import logging
import logging.config
import yaml
import os

def setup_logging(
    default_path='logging.yaml',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """
    Configure le système de logging à partir d'un fichier YAML.
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value

    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        logging.warning("Le fichier de configuration du logging est introuvable. Utilisation de la configuration par défaut.")
