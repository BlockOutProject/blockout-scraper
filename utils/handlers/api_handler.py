from functools import wraps
import logging
from typing import Callable, Optional, Type, Union, get_args, get_origin
import aiohttp

logger = logging.getLogger('blockout')

def handle_api_response(response_type: Optional[Type] = None) -> Callable:
    """
    Décorateur pour gérer les réponses API et les erreurs.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Optional[Union[dict, object]]:
            try:
                # Appel de la fonction originale
                response = await func(*args, **kwargs)

                # Vérifier si la réponse est une réussite (200 ou 201)
                if response.status in {200, 201}:
                    if response.content_type:  # Vérifie si un type de contenu est défini
                        if response.content_type == "application/json":
                            json_data = await response.json()
                            if response_type:
                                # Traiter les types complexes comme des listes ou des objets
                                if get_origin(response_type) is list:
                                    item_type = get_args(response_type)[0]
                                    return [item_type(**item) for item in json_data]
                                return response_type(**json_data)
                            return json_data
                    # Aucun contenu JSON, retourner None pour une réponse valide
                    return None

                # Gérer les cas où l'API renvoie 204 No Content
                elif response.status == 204:
                    return None

                # Gérer les erreurs API (4xx et 5xx)
                else:
                    error_data = await response.json()
                    error_message = error_data.get("message", "Message d'erreur non spécifié")
                    logger.error(f"Erreur {response.status}: {error_message}")
                    return None

            except aiohttp.ClientError as e:
                # Gérer les erreurs réseau ou autres erreurs liées à aiohttp
                logger.error(f"Erreur réseau: {str(e)}")
                return None

        return wrapper
    return decorator