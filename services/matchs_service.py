from typing import Optional
import aiohttp
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from api.matchs_api import create_match, deactivate_match, get_active_matches_by_pool_id, get_match_by_league_and_code, get_started_matches, update_match
from errors_handler import handle_errors
import logging
from models.match import Match, MatchStatus

logger = logging.getLogger('blockout')

async def add_or_update_match(session: aiohttp.ClientSession, match_data: dict):
    """
    Vérifie l'existence d'un match et le met à jour ou le crée selon les besoins.
    """
    required_fields = ['league_code', 'match_code', 'pool_id', 'team_id_a', 'team_id_b', 'match_date']

    # Validation des champs obligatoires
    for field in required_fields:
        if field not in match_data or not match_data[field]:
            raise ValueError(f"{field} est obligatoire pour ajouter ou mettre à jour un match.")

    # Convertir datetime en ISO 8601 si nécessaire
    if 'match_date' in match_data and isinstance(match_data['match_date'], datetime):
        match_data['match_date'] = match_data['match_date'].isoformat()

    # Vérifier si le match existe déjà
    existing_match = await get_match_by_league_and_code(session, match_data['league_code'], match_data['match_code'])
    
    if existing_match:
        # Vérifier les changements
        changes = []

        if existing_match['team_id_a'] != match_data['team_id_a']:
            changes.append(f"team_id_a: {existing_match['team_id_a']} -> {match_data['team_id_a']}")
        
        if existing_match['team_id_b'] != match_data['team_id_b']:
            changes.append(f"team_id_b: {existing_match['team_id_b']} -> {match_data['team_id_b']}")
        
        if existing_match['match_date'] != match_data['match_date']:
            changes.append(f"match_date: {existing_match['match_date']} -> {match_data['match_date']}")
        
        if existing_match['set'] != match_data.get('set'):
            changes.append(f"set: {existing_match['set']} -> {match_data.get('set')}")

        if existing_match['score'] != match_data.get('score'):
            changes.append(f"score: {existing_match['score']} -> {match_data.get('score')}")

        if existing_match['status'] != match_data.get('status'):
            changes.append(f"status: {existing_match['status']} -> {match_data.get('status')}")

        if existing_match['venue'] != match_data.get('venue'):
            changes.append(f"venue: {existing_match['venue']} -> {match_data.get('venue')}")

        if existing_match['referee1'] != match_data.get('referee1'):
            changes.append(f"referee1: {existing_match['referee1']} -> {match_data.get('referee1')}")

        if existing_match['referee2'] != match_data.get('referee2'):
            changes.append(f"referee2: {existing_match['referee2']} -> {match_data.get('referee2')}")

        # Si des changements existent, on met à jour le match
        if changes:
            return await update_match(session, existing_match['id'], match_data)
        else:
            return existing_match
    else:
        # Si le match n'existe pas, on le crée
        return await create_match(session, match_data)

async def deactivate_matches(session: aiohttp.ClientSession, pool_id: int, scraped_match_codes: set):
    """
    Désactive les matchs qui existent en base mais n'ont pas été scrapés pour une pool spécifique.

    Parameters:
    - session: La session HTTP asynchrone.
    - pool_id: L'ID de la pool dont on veut désactiver les matchs.
    - scraped_match_codes (set): Un ensemble des codes de matchs qui ont été scrapés pour cette pool.
    """
    # Récupérer tous les matchs actifs pour la pool donnée
    matches = await get_active_matches_by_pool_id(session, pool_id)
    if matches is None:
        return

    # Filtrer les matchs qui n'ont pas été scrapés
    matches_to_deactivate = [match for match in matches if match['match_code'] not in scraped_match_codes]

    # Désactiver ces matchs via des requêtes PUT
    for match in matches_to_deactivate:
        await deactivate_match(session, match)

async def log_started_matches():
    """
    Logue les matchs qui ont commencé.
    """
    current_time = datetime.now(timezone.utc).isoformat()

    async with aiohttp.ClientSession() as session:
        started_matches = await get_started_matches(session, 'UPCOMING', True, current_time)

        if started_matches:
            logger.info("Matchs en cours :")
            for match in started_matches:
                logger.info(f"Match {match['match_code']} dans la ligue {match['league_code']}: "
                            f"équipe A ({match['team_id_a']}) vs équipe B ({match['team_id_b']}) "
                            f"à {match['match_date']} à {match['venue']}")
        else:
            logger.info("Aucun match en cours trouvé.")
