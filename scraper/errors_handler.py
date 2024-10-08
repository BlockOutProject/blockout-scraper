# errors_handler.py
import functools
import asyncio
import logging

# Importer le logger configuré
logger = logging.getLogger('myvolley')

def handle_errors(func):
    """
    Décorateur pour gérer les erreurs des fonctions synchrones et asynchrones.
    Log l'erreur avec la trace complète et continue l'exécution.
    """
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Erreur dans la fonction asynchrone '{func.__name__}': {e}",
                    exc_info=True
                )
                return None
        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Erreur dans la fonction synchrone '{func.__name__}': {e}",
                    exc_info=True
                )
                return None
        return sync_wrapper