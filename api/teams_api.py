import aiohttp
import logging

from api_handler import handle_api_response

logger = logging.getLogger('blockout')

TEAM_API_URL = 'http://localhost:8082/api/teams'

@handle_api_response
async def get_team_by_pool_and_name(session: aiohttp.ClientSession, pool_id: int, team_name: str):
    """
    Vérifie si une équipe existe déjà via l'API en utilisant pool_id et team_name.

    Parameters:
    - session: La session HTTP asynchrone.
    - pool_id (int): L'ID de la pool.
    - team_name (str): Le nom de l'équipe.

    Returns:
    - dict: L'équipe existante si trouvée, None sinon.
    """
    params = {'pool_id': pool_id, 'team_name': team_name}
    return await session.get(f"{TEAM_API_URL}/search", params=params)


@handle_api_response
async def create_team(session: aiohttp.ClientSession, team_data: dict):
    """
    Envoie une requête POST pour créer une nouvelle équipe.

    Parameters:
    - session: La session HTTP asynchrone.
    - team_data (dict): Les données de l'équipe à créer.

    Returns:
    - dict: L'équipe créée si ajoutée avec succès.
    """
    return await session.post(TEAM_API_URL, json=team_data)


@handle_api_response
async def update_team(session: aiohttp.ClientSession, team_id: int, team_data: dict, changes: list = []):
    """
    Envoie une requête PUT pour mettre à jour une équipe existante.

    Parameters:
    - session: La session HTTP asynchrone.
    - team_id (int): L'ID de l'équipe à mettre à jour.
    - team_data (dict): Les données mises à jour de l'équipe.

    Returns:
    - dict: L'équipe mise à jour si elle est modifiée avec succès.
    """
    return await session.put(f"{TEAM_API_URL}/{team_id}", json=team_data)

@handle_api_response
async def get_active_teams_by_pool_id(session, pool_id):
    """Récupère les équipes actives pour une pool donnée."""
    return await session.get(f"{TEAM_API_URL}/active?pool_id={pool_id}")


@handle_api_response
async def deactivate_team(session, team):
    """Désactive une équipe en mettant à jour son statut 'active' à False."""
    team['active'] = False
    return await session.put(f"{TEAM_API_URL}/{team['id']}", json=team)