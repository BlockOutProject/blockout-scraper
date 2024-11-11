from dataclasses import asdict
from typing import Optional
import aiohttp
import logging
from utils.handlers.api_handler import handle_api_response
from models.team import Team

logger = logging.getLogger('blockout')

TEAM_API_URL = 'http://localhost:8082/api/teams'

@handle_api_response(response_type=Team)
async def get_team_by_pool_and_name(session: aiohttp.ClientSession, pool_id: int, team_name: str) -> Optional[Team]:
    """
    Vérifie si une équipe existe déjà via l'API en utilisant pool_id et team_name.
    """
    try:
        params = {'pool_id': pool_id, 'team_name': team_name}
        return await session.get(f"{TEAM_API_URL}/search", params=params)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'équipe (pool_id={pool_id}, team_name={team_name}): {e}")
        raise

@handle_api_response(response_type=Team)
async def create_team(session: aiohttp.ClientSession, team: Team) -> Optional[Team]:
    """
    Envoie une requête POST pour créer une nouvelle équipe.
    """
    try:
        team_dict = asdict(team)
        response = await session.post(TEAM_API_URL, json=team_dict)
        logger.info(f"Équipe {team.team_name} (club_id: {team.club_id}) créée avec succès.")
        return response
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'équipe {team.team_name}: {e}")
        raise

@handle_api_response(response_type=Team)
async def update_team(session: aiohttp.ClientSession, team: Team, changes: list[str] = []) -> Optional[Team]:
    """
    Envoie une requête PUT pour mettre à jour une équipe existante.
    """
    try:
        team_dict = asdict(team)
        response = await session.put(f"{TEAM_API_URL}/{team.id}", json=team_dict)
        
        if changes:
            logger.info(f"Équipe {team.team_name} (ID: {team.id}) mise à jour avec les changements suivants: {', '.join(changes)}")
        
        return response
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de l'équipe {team.team_name} (ID: {team.id}): {e}")
        raise

@handle_api_response(response_type=list[Team])
async def get_active_teams_by_pool_id(session: aiohttp.ClientSession, pool_id: int) -> Optional[list[Team]]:
    """
    Récupère les équipes actives pour une pool donnée.
    """
    try:
        return await session.get(f"{TEAM_API_URL}/active?pool_id={pool_id}")
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des équipes actives pour la pool {pool_id}: {e}")
        raise

@handle_api_response(response_type=None)
async def deactivate_team(session: aiohttp.ClientSession, team_id: int) -> None:
    """
    Désactive une équipe en mettant à jour son statut 'active' à False.
    """
    try:
        await session.put(f"{TEAM_API_URL}/{team_id}/deactivate")
        logger.info(f"Équipe {team_id} désactivée avec succès.")
    except Exception as e:
        logger.error(f"Erreur lors de la désactivation de l'équipe (ID: {team_id}): {e}")
        raise