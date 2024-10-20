import aiohttp
import logging
from api.matchs_api import deactivate_match, get_active_matches_by_pool_id
from api.teams_api import deactivate_team, get_active_teams_by_pool_id

from api_handler import handle_api_response

logger = logging.getLogger('blockout')

POOL_API_URL = 'http://localhost:8081/api/pools'
TEAM_API_URL = 'http://localhost:8082/api/teams'
MATCH_API_URL = 'http://localhost:8083/api/matches'

@handle_api_response
async def get_pool_by_code_league_season(session: aiohttp.ClientSession, pool_code: str, league_code: str, season: int):
    """
    Vérifie si une pool existe déjà via l'API en utilisant pool_code, league_code et season.
    """
    return await session.get(f"{POOL_API_URL}/{pool_code}/{league_code}/{season}")

@handle_api_response
async def create_pool(session: aiohttp.ClientSession, pool_data: dict):
    """
    Envoie une requête POST pour créer une nouvelle pool.
    """
    return await session.post(POOL_API_URL, json=pool_data)

@handle_api_response
async def update_pool(session: aiohttp.ClientSession, pool_id: int, pool_data: dict):
    """
    Envoie une requête PUT pour mettre à jour une pool existante.
    """
    return await session.put(f"{POOL_API_URL}/{pool_id}", json=pool_data)

@handle_api_response
async def get_active_pools_by_league_code(session, league_code):
    """Récupère les pools actives pour une ligue donnée."""
    return await session.get(f"{POOL_API_URL}/active?league_code={league_code}")

async def deactivate_pool(session, pool):
    """Désactive une pool en mettant à jour son statut 'active' à False."""
    pool['active'] = False
    await update_pool(session, pool['id'], pool)

async def deactivate_pools(session, league_code, scraped_pool_codes):
    """
    Désactive les pools, équipes et matchs qui existent en base mais n'ont pas été scrapés.
    """
    pools = await get_active_pools_by_league_code(session, league_code)
    if pools is None:
        return

    pools_to_deactivate = [pool for pool in pools if pool['pool_code'] not in scraped_pool_codes]
    pool_ids_to_deactivate = [pool['id'] for pool in pools_to_deactivate]

    # Désactiver les équipes associées aux pools désactivées
    for pool_id in pool_ids_to_deactivate:
        teams = await get_active_teams_by_pool_id(session, pool_id)
        if teams:
            for team in teams:
                await deactivate_team(session, team)

    # Désactiver les matchs associés aux pools désactivées
    for pool_id in pool_ids_to_deactivate:
        matches = await get_active_matches_by_pool_id(session, pool_id)
        if matches:
            for match in matches:
                await deactivate_match(session, match)

    # Désactiver les pools
    for pool in pools_to_deactivate:
        await deactivate_pool(session, pool)