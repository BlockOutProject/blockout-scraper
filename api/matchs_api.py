import aiohttp
import logging
from datetime import datetime
from functools import wraps

from api_handler import handle_api_response

logger = logging.getLogger('blockout')

MATCH_API_URL = 'http://localhost:8083/api/matches'

@handle_api_response
async def get_match_by_league_and_code(session: aiohttp.ClientSession, league_code: str, match_code: str):
    """
    Vérifie si un match existe déjà via l'API en utilisant league_code et match_code.
    """
    return await session.get(f"{MATCH_API_URL}/{league_code}/{match_code}")

@handle_api_response
async def create_match(session: aiohttp.ClientSession, match_data: dict):
    """
    Envoie une requête POST pour créer un nouveau match.
    """
    return await session.post(MATCH_API_URL, json=match_data)

@handle_api_response
async def update_match(session: aiohttp.ClientSession, match_id: int, match_data: dict):
    """
    Envoie une requête PUT pour mettre à jour un match existant.
    """
    return await session.put(f"{MATCH_API_URL}/{match_id}", json=match_data)

@handle_api_response
async def get_active_matches_by_pool_id(session, pool_id):
    """Récupère les matchs actifs pour une pool donnée."""
    return await session.get(f"{MATCH_API_URL}/active?pool_id={pool_id}")

@handle_api_response
async def deactivate_match(session, match):
    """Désactive un match en mettant à jour son statut 'active' à False."""
    match['active'] = False
    return await session.put(f"{MATCH_API_URL}/{match['id']}", json=match)

@handle_api_response
async def get_started_matches(session: aiohttp.ClientSession, status: str, active: bool, current_time: str):
    """
    Récupère les matchs qui ont commencé via l'API.

    Parameters:
    - session: La session HTTP asynchrone.
    - status (str): Le statut du match (UPCOMING).
    - active (bool): Si le match est actif ou non.
    - current_time (str): L'heure actuelle au format ISO8601 pour filtrer les matchs.

    Returns:
    - list: Une liste des matchs commencés si elle est trouvée, None sinon.
    """
    params = {
        'status': status,
        'active': str(active).lower(),
        'current_time': current_time
    }

    return await session.get(f"{MATCH_API_URL}/started", params=params)