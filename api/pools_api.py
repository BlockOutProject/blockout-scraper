from typing import Optional, List
import aiohttp
import logging
from utils.handlers.error_handler import handle_errors
from utils.handlers.api_handler import handle_api_response
from models.pool import Pool

logger = logging.getLogger('blockout')

POOL_API_URL = 'http://localhost:8081/api/pools'


@handle_errors
@handle_api_response(response_type=Pool)
async def get_pool_by_code_league_season(
    session: aiohttp.ClientSession, pool_code: str, league_code: str, season: int
) -> Optional[Pool]:
    """
    Vérifie si une pool existe déjà via l'API en utilisant pool_code, league_code et season.
    """
    return await session.get(f"{POOL_API_URL}/{pool_code}/{league_code}/{season}")

@handle_errors
@handle_api_response(response_type=List[Pool])
async def get_pools_by_league_and_season(session: aiohttp.ClientSession, league_code: str, season: int) -> List[Pool]:
    """
    Récupère toutes les pools pour un code de ligue et une saison spécifiques.
    """
    url = f"{POOL_API_URL}/league/{league_code}/season/{season}"
    return await session.get(url)

@handle_errors
@handle_api_response(response_type=Pool)
async def create_pool(session: aiohttp.ClientSession, pool: Pool) -> Optional[Pool]:
    """
    Envoie une requête POST pour créer une nouvelle pool.
    """
    pool_dict = pool.to_dict()
    response = await session.post(POOL_API_URL, json=pool_dict)
    logger.info(f"Pool {pool.pool_code} (division: {pool.division_name}) créée avec succès.")
    return response


@handle_errors
@handle_api_response(response_type=Pool)
async def update_pool(session: aiohttp.ClientSession, pool: Pool, changes: List[str] = []) -> Optional[Pool]:
    """
    Envoie une requête PUT pour mettre à jour une pool existante.
    """
    pool_dict = pool.to_dict()
    response = await session.put(f"{POOL_API_URL}/{pool.id}", json=pool_dict)

    if changes:
        logger.info(f"Pool {pool.pool_code} (ID: {pool.id}) mise à jour avec les changements suivants: {', '.join(changes)}")
    return response


@handle_errors
@handle_api_response(response_type=List[Pool])
async def get_active_pools_by_league_code(session: aiohttp.ClientSession, league_code: str) -> Optional[List[Pool]]:
    """
    Récupère les pools actives pour une ligue donnée.
    """
    return await session.get(f"{POOL_API_URL}/active?league_code={league_code}")


@handle_errors
@handle_api_response(response_type=None)
async def deactivate_pool(session: aiohttp.ClientSession, pool_id: int) -> None:
    """
    Désactive une pool en mettant à jour son statut 'active' à False.
    """
    await session.put(f"{POOL_API_URL}/{pool_id}/deactivate")
    logger.info(f"Requête envoyée pour désactiver la pool {pool_id}.")