from typing import Optional
import aiohttp
from api.teams_api import create_team, deactivate_team, get_active_teams_by_pool_id, get_team_by_pool_and_name, update_team
import logging
from models.team import Team
from utils.handlers.function_name_handler import log_function_name

logger = logging.getLogger('blockout')

@log_function_name
async def add_or_update_team(session: aiohttp.ClientSession, team: Team) -> Optional[Team]:
    """
    Vérifie l'existence d'une équipe et la met à jour ou la crée selon les besoins.
    """
    try:
        # Validation des champs obligatoires
        required_fields = ['pool_id', 'team_name']
        missing_fields = [field for field in required_fields if not getattr(team, field, None)]
        if missing_fields:
            raise ValueError(f"Les champs obligatoires suivants sont manquants : {', '.join(missing_fields)}.")

        # Vérification de l'existence de l'équipe
        existing_team = await get_team_by_pool_and_name(session, team.pool_id, team.team_name)

        if existing_team:
            # Mise à jour si l'équipe existe déjà
            changes = []
            team.id = existing_team.id

            # Vérifier les changements
            if existing_team.club_id != team.club_id:
                changes.append(f"club_id: {existing_team.club_id} -> {team.club_id}")

            if not existing_team.active:
                team.active = True
                changes.append("Équipe réactivée")

            if changes:
                logger.info(f"Équipe {existing_team.team_name} mise à jour avec les changements : {', '.join(changes)}")
                return await update_team(session, team, changes)
            else:
                return existing_team
        else:
            # Création d'une nouvelle équipe
            new_team = await create_team(session, team)
            logger.info(f"Équipe {team.team_name} créée avec succès.")
            return new_team

    except ValueError as ve:
        logger.error(f"[add_or_update_team] Validation échouée : {ve}")
        raise
    except Exception as e:
        logger.error(f"[add_or_update_team] Erreur inattendue : {e}")
        raise

@log_function_name
async def deactivate_teams(session: aiohttp.ClientSession, pool_id: int, scraped_team_names: set) -> None:
    """
    Désactive les équipes qui existent en base mais n'ont pas été scrapées pour une pool spécifique.

    Parameters:
    - session: La session HTTP asynchrone.
    - pool_id: L'ID de la pool dont on veut désactiver les équipes.
    - scraped_team_names (set): Un ensemble des noms d'équipes qui ont été scrapées pour cette pool.
    """
    try:
        # Récupérer toutes les équipes actives pour la pool donnée
        teams = await get_active_teams_by_pool_id(session, pool_id)
        if not teams:
            return

        # Filtrer les équipes qui n'ont pas été scrapées
        teams_to_deactivate = [team for team in teams if team.team_name not in scraped_team_names]

        # Désactiver ces équipes via des requêtes PUT
        for team in teams_to_deactivate:
            try:
                await deactivate_team(session, team.id)
                logger.info(f"Équipe {team.team_name} (ID: {team.id}) désactivée avec succès.")
            except Exception as e:
                logger.error(f"Erreur lors de la désactivation de l'équipe {team.team_name} (ID: {team.id}): {e}")
                continue

    except Exception as e:
        logger.error(f"[deactivate_teams] Erreur inattendue lors de la désactivation des équipes pour la pool {pool_id}: {e}")
        raise