import aiohttp
import logging
from functools import wraps

logger = logging.getLogger('blockout')

import aiohttp
import logging
from functools import wraps

logger = logging.getLogger('blockout')

def handle_api_response(func):
    """Décorateur pour gérer les réponses API et les erreurs"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Appel de la fonction originale
            response = await func(*args, **kwargs)
            
            # Vérifier si la requête a réussi avec du contenu
            if response.status in {200, 201}:
                json_data = await response.json()
                return json_data  # Retourner les données JSON en cas de succès
            
            # Gérer le cas où l'API renvoie 204 No Content
            elif response.status == 204:
                return None  # Retourner None car il n'y a pas de contenu à traiter
            
            # Gérer les erreurs API (autres statuts 4xx et 5xx)
            else:
                error_data = await response.json()
                error_message = error_data.get('message', 'Message d\'erreur non spécifié')
                logger.error(f"Erreur {response.status}: {error_message}")
                return None

        except aiohttp.ClientError as e:
            # Gérer les erreurs réseau ou liées à aiohttp
            logger.error(f"Erreur réseau: {str(e)}")
            return None

    return wrapper