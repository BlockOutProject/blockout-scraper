import aiohttp
import logging
from datetime import datetime
from typing import Optional, List

from models.match import Match, MatchStatus
from utils.handlers.error_handler import handle_errors
from utils.handlers.api_handler import handle_api_response

logger = logging.getLogger('blockout')

MATCH_API_URL = 'http://localhost:8083/api/matches'


@handle_errors
@handle_api_response(response_type=Match)
async def get_match_by_league_and_code(session: aiohttp.ClientSession, league_code: str, match_code: str) -> Optional[Match]:
    return await session.get(f"{MATCH_API_URL}/{league_code}/{match_code}")


@handle_errors
@handle_api_response(response_type=List[Match])
async def get_active_matches_by_pool_id(session: aiohttp.ClientSession, pool_id: int) -> Optional[List[Match]]:
    """
    Récupère les matchs actifs pour une pool donnée.
    """
    return await session.get(f"{MATCH_API_URL}/active?pool_id={pool_id}")


@handle_errors
@handle_api_response(response_type=Match)
async def create_match(session: aiohttp.ClientSession, match: Match) -> Optional[Match]:
    """
    Envoie une requête POST pour créer un nouveau match.
    """
    match_dict = match.to_dict()
    response = await session.post(MATCH_API_URL, json=match_dict)
    logger.info(f"Match {match.match_code} (pool_id: {match.pool_id}) créé avec succès.")
    return response


@handle_errors
@handle_api_response(response_type=Match)
async def update_match(session: aiohttp.ClientSession, match: Match, changes: List[str] = []) -> Optional[Match]:
    """
    Envoie une requête PUT pour mettre à jour un match existant.
    """
    match_dict = match.to_dict()
    response = await session.put(f"{MATCH_API_URL}/{match.id}", json=match_dict)
    if changes:
        logger.info(f"Match {match.match_code} (ID: {match.id}) mis à jour avec les changements suivants: {', '.join(changes)}")
    return response


@handle_errors
@handle_api_response(response_type=None)
async def deactivate_match(session: aiohttp.ClientSession, match_id: int) -> None:
    """
    Désactive un match en envoyant une requête PUT à une route dédiée.
    """
    await session.put(f"{MATCH_API_URL}/{match_id}/deactivate")
    logger.info(f"Match {match_id} désactivé avec succès.")


@handle_errors
@handle_api_response(response_type=List[Match])
async def get_started_matches(session: aiohttp.ClientSession, status: MatchStatus, active: bool, current_time: str) -> Optional[List[Match]]:
    """
    Récupère les matchs qui ont commencé via l'API.
    """
    params = {
        'status': status,
        'active': str(active).lower(),
        'current_time': current_time
    }
    return await session.get(f"{MATCH_API_URL}/started", params=params)


@handle_errors
@handle_api_response(response_type=Match)
async def get_match_by_pool_teams_date(
    session: aiohttp.ClientSession,
    pool_id: int,
    team_id_a: int,
    team_id_b: int,
    match_date: datetime
) -> Optional[Match]:
    """
    Récupère un match spécifique basé sur pool_id, team_id_a, team_id_b et match_date.
    """
    params = {
        'pool_id': pool_id,
        'team_id_a': team_id_a,
        'team_id_b': team_id_b,
        'match_date': match_date.isoformat()
    }
    return await session.get(f"{MATCH_API_URL}/search", params=params)