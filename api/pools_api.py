from dataclasses import asdict
from typing import Optional
import aiohttp
import logging
from utils.handlers.api_handler import handle_api_response
from models.pool import Pool

logger = logging.getLogger('blockout')

POOL_API_URL = 'http://localhost:8081/api/pools'
TEAM_API_URL = 'http://localhost:8082/api/teams'
MATCH_API_URL = 'http://localhost:8083/api/matches'

@handle_api_response(response_type=Pool)
async def get_pool_by_code_league_season(session: aiohttp.ClientSession, pool_code: str, league_code: str, season: int) -> Optional[Pool]:
    """
    Vérifie si une pool existe déjà via l'API en utilisant pool_code, league_code et season.
    """
    try:
        return await session.get(f"{POOL_API_URL}/{pool_code}/{league_code}/{season}")
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la pool (pool_code={pool_code}, league_code={league_code}, season={season}): {e}")
        raise

@handle_api_response(response_type=Pool)
async def create_pool(session: aiohttp.ClientSession, pool: Pool) -> Optional[Pool]:
    """
    Envoie une requête POST pour créer une nouvelle pool.
    """
    try:
        pool_dict = asdict(pool)
        response = await session.post(POOL_API_URL, json=pool_dict)
        logger.info(f"Pool {pool.pool_code} (division: {pool.division_name}) créée avec succès.")
        return response
    except Exception as e:
        logger.error(f"Erreur lors de la création de la pool {pool.pool_code}: {e}")
        raise

@handle_api_response(response_type=Pool)
async def update_pool(session: aiohttp.ClientSession, pool: Pool, changes: list = []) -> Optional[Pool]:
    """
    Envoie une requête PUT pour mettre à jour une pool existante.
    """
    try:
        pool_dict = asdict(pool)
        response = await session.put(f"{POOL_API_URL}/{pool.id}", json=pool_dict)
        
        if changes:
            logger.info(f"Pool {pool.pool_code} (ID: {pool.id}) mise à jour avec les changements suivants: {', '.join(changes)}")
        return response
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la pool {pool.pool_code} (ID: {pool.id}): {e}")
        raise

@handle_api_response(response_type=list[Pool])
async def get_active_pools_by_league_code(session: aiohttp.ClientSession, league_code: str) -> Optional[list[Pool]]:
    """
    Récupère les pools actives pour une ligue donnée.
    """
    try:
        return await session.get(f"{POOL_API_URL}/active?league_code={league_code}")
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des pools actives pour la ligue {league_code}: {e}")
        raise

@handle_api_response(response_type=None)
async def deactivate_pool(session: aiohttp.ClientSession, pool_id: int) -> None:
    """
    Désactive une pool en mettant à jour son statut 'active' à False.
    """
    try:
        await session.put(f"{POOL_API_URL}/{pool_id}/deactivate")
        logger.info(f"Requête envoyée pour désactiver la pool {pool_id}.")
    except Exception as e:
        logger.error(f"Erreur lors de la désactivation de la pool (ID: {pool_id}): {e}")
        raise