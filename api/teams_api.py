from dataclasses import asdict
from typing import Optional
import aiohttp
import logging
from api_handler import handle_api_response
from models.team import Team

logger = logging.getLogger('blockout')

TEAM_API_URL = 'http://localhost:8082/api/teams'

@handle_api_response(response_type=Team)
async def get_team_by_pool_and_name(session: aiohttp.ClientSession, pool_id: int, team_name: str) -> Optional[Team]:
    """
    Vérifie si une équipe existe déjà via l'API en utilisant pool_id et team_name.
    """
    params = {'pool_id': pool_id, 'team_name': team_name}
    return await session.get(f"{TEAM_API_URL}/search", params=params)

@handle_api_response(response_type=Team)
async def create_team(session: aiohttp.ClientSession, team: Team) -> Optional[Team]:
    """
    Envoie une requête POST pour créer une nouvelle équipe.
    """
    team_dict = asdict(team)

    response = await session.post(TEAM_API_URL, json=team_dict)
    logger.info(f"Équipe {team.team_name} (club_id: {team.club_id}) créée avec succès.")
    return response

@handle_api_response(response_type=Team)
async def update_team(session: aiohttp.ClientSession, team: Team, changes: list[str] = []) -> Optional[Team]:
    """
    Envoie une requête PUT pour mettre à jour une équipe existante.
    """
    team_dict = asdict(team)

    response = await session.put(f"{TEAM_API_URL}/{team.id}", json=team_dict)
    
    if changes:
        logger.info(f"Équipe {team.team_name} (ID: {team.id}) mise à jour avec les changements suivants: {', '.join(changes)}")
    
    return response

@handle_api_response(response_type=list[Team])
async def get_active_teams_by_pool_id(session: aiohttp.ClientSession, pool_id: int) -> Optional[list[Team]]:
    """
    Récupère les équipes actives pour une pool donnée.
    """
    return await session.get(f"{TEAM_API_URL}/active?pool_id={pool_id}")

@handle_api_response(response_type=None)
async def deactivate_team(session: aiohttp.ClientSession, team_id: int) -> None:
    """
    Désactive une équipe en mettant à jour son statut 'active' à False.
    """
    await session.put(f"{TEAM_API_URL}/{team_id}/deactivate")
    logger.info(f"Équipe {team_id} désactivée avec succès.")