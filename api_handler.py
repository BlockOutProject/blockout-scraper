import aiohttp
import logging
from functools import wraps
from typing import Type, Optional, Callable, Union, get_origin, get_args

logger = logging.getLogger('blockout')

def handle_api_response(response_type: Optional[Type] = None) -> Callable:
    """
    Décorateur pour gérer les réponses API et les erreurs.

    Parameters:
    - response_type (Type, optional): Type de retour souhaité, s'il est spécifié, 
      les données JSON seront converties en une instance de ce type.

    Returns:
    - Callable: Une fonction décorée gérant la réponse API.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Optional[Union[dict, object]]:
            try:
                # Appel de la fonction originale
                response = await func(*args, **kwargs)
                
                # Vérifier si la requête a réussi avec du contenu
                if response.status in {200, 201}:
                    json_data = await response.json()
                    
                    # Si un type de retour est spécifié, instancier cet objet avec les données JSON
                    if response_type:
                        # Vérifie si response_type est une liste d'un type spécifique
                        if get_origin(response_type) is list:
                            item_type = get_args(response_type)[0]  # Le type d'éléments dans la liste
                            return [item_type(**item) for item in json_data]
                        return response_type(**json_data)
                    return json_data

                    
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
    return decorator