from typing import Optional
import aiohttp
from sqlalchemy.orm import Session
from api.teams_api import create_team, deactivate_team, get_active_teams_by_pool_id, get_team_by_pool_and_name, update_team
import logging
from models.team import Team

logger = logging.getLogger('blockout')

async def add_or_update_team(session: aiohttp.ClientSession, team: Team):
    """
    Vérifie l'existence d'une équipe et la met à jour ou la crée selon les besoins.

    Parameters:
    - session: La session HTTP asynchrone.
    - team (dict): Les données de l'équipe à ajouter ou mettre à jour.

    Returns:
    - dict: L'équipe ajoutée ou mise à jour.
    """
    required_fields = ['pool_id', 'team_name']

    # Validation des champs obligatoires
    for field in required_fields:
        if not getattr(team, field, None):
            raise ValueError(f"{field} est obligatoire pour ajouter ou mettre à jour une équipe.")

    # Vérifier si l'équipe existe déjà
    existing_team = await get_team_by_pool_and_name(session, team.pool_id, team.team_name)
    if existing_team:

        changes = []
        
        team.id = existing_team.id

        if existing_team.club_id != team.club_id:
            changes.append(f"club_id: {existing_team.club_id} -> {team.club_id}")

        if not existing_team.active:
            changes.append("Équipe réactivée")
            team.active = True

        if changes:
            return await update_team(session, team, changes)
        else:
            return existing_team
    else:
        # Si l'équipe n'existe pas, on la crée
        return await create_team(session, team)


async def deactivate_teams(session: aiohttp.ClientSession, pool_id: int, scraped_team_names: set) -> None:
    """
    Désactive les équipes qui existent en base mais n'ont pas été scrapées pour une pool spécifique.

    Parameters:
    - session: La session HTTP asynchrone.
    - pool_id: L'ID de la pool dont on veut désactiver les équipes.
    - scraped_team_names (set): Un ensemble des noms d'équipes qui ont été scrapés pour cette pool.
    """
    # Récupérer toutes les équipes actives pour la pool donnée
    teams = await get_active_teams_by_pool_id(session, pool_id)
    if teams is None:
        return

    # Filtrer les équipes qui n'ont pas été scrapées
    teams_to_deactivate = [team for team in teams if team.team_name not in scraped_team_names]

    # Désactiver ces équipes via des requêtes PUT
    for team in teams_to_deactivate:
        await deactivate_team(session, team.id)