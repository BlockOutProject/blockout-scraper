from typing import Optional
import aiohttp
from api.teams_api import create_team, deactivate_team, get_active_teams_by_pool_id, get_team_by_pool_and_name, update_team
import logging
from models.team import Team
from utils.handlers.error_handler import handle_errors

logger = logging.getLogger('blockout')

@handle_errors
async def add_or_update_team(session: aiohttp.ClientSession, team: Team, existing_team: Optional[Team]) -> Optional[Team]:
    """
    Vérifie l'existence d'une équipe et la met à jour ou la crée selon les besoins.
    """
    required_fields = ['pool_id', 'team_name']
    missing_fields = [field for field in required_fields if not getattr(team, field, None)]
    if missing_fields:
        raise ValueError(f"Les champs obligatoires suivants sont manquants : {', '.join(missing_fields)}.")

    if existing_team:
        team.id = existing_team.id
        changes = []
        if existing_team.club_id != team.club_id:
            changes.append(f"club_id: {existing_team.club_id} -> {team.club_id}")
        if not existing_team.active:
            team.active = True
            changes.append("Équipe réactivée")
        if changes:
            return await update_team(session, team, changes)
        return existing_team
    else:
        new_team = await create_team(session, team)
        logger.info(f"Équipe {team.team_name} créée avec succès.")
        return new_team


@handle_errors
async def deactivate_teams(session: aiohttp.ClientSession, pool_id: int, scraped_team_names: set) -> None:
    """
    Désactive les équipes qui existent en base mais n'ont pas été scrapées pour une pool spécifique.
    """
    if not isinstance(pool_id, int) or pool_id <= 0:
        raise ValueError(f"pool_id invalide : {pool_id}")

    teams = await get_active_teams_by_pool_id(session, pool_id)
    if not teams:
        return

    teams_to_deactivate = [team for team in teams if team.team_name not in scraped_team_names]
    for team in teams_to_deactivate:
        try:
            await deactivate_team(session, team.id)
            logger.info(f"Équipe {team.team_name} (ID: {team.id}) désactivée avec succès.")
        except Exception as e:
            logger.error(f"Erreur lors de la désactivation de l'équipe {team.team_name} (ID: {team.id}): {e}")