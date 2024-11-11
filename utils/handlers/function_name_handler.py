from functools import wraps
import logging

logger = logging.getLogger('blockout')

def log_function_name(func):
    """Décorateur pour ajouter le nom de la fonction dans les logs en cas d'erreur."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            function_name = func.__name__
            logger.error(f"[{function_name}] Erreur: {e}")
            raise
    return wrapper