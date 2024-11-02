from typing import Optional, Set, Dict
import aiohttp
from datetime import datetime, timezone
from api.matchs_api import create_match, deactivate_match, get_active_matches_by_pool_id, get_match_by_league_and_code, get_started_matches, update_match
import logging
from models.match import Match, MatchStatus

logger = logging.getLogger('blockout')

async def add_or_update_match(session: aiohttp.ClientSession, match: Match) -> Optional[Match]:
    """
    Vérifie l'existence d'un match et le met à jour ou le crée selon les besoins.
    """
    required_fields = ['league_code', 'match_code', 'pool_id', 'team_id_a', 'team_id_b', 'match_date']

    for field in required_fields:
        if not getattr(match, field, None):
            raise ValueError(f"{field} est obligatoire pour ajouter ou mettre à jour un match.")

    # Convertir datetime en ISO 8601 si nécessaire
    if match.match_date and isinstance(match.match_date, datetime):
        match.match_date = match.match_date.isoformat()

    existing_match = await get_match_by_league_and_code(session, match.league_code, match.match_code)
    
    if existing_match:
        changes = []
        match.id = existing_match.id
        
        if not existing_match.active:
            changes.append(f"Match {existing_match.match_code} (ID: {existing_match.id}) réactivé avec succès.")

        if existing_match.team_id_a != match.team_id_a:
            changes.append(f"team_id_a: {existing_match.team_id_a} -> {match.team_id_a}")
        
        if existing_match.team_id_b != match.team_id_b:
            changes.append(f"team_id_b: {existing_match.team_id_b} -> {match.team_id_b}")
        
        if match.league_code != 'AALNV' and existing_match.match_date != match.match_date: # On ignore la date pour les matchs pro car elle est traitée dans le lnv scraper
            changes.append(f"match_date: {existing_match.match_date} -> {match.match_date}")
        
        if existing_match.set != match.set:
            changes.append(f"set: {existing_match.set} -> {match.set}")

        if existing_match.score != match.score:
            changes.append(f"score: {existing_match.score} -> {match.score}")

        if existing_match.status != match.status:
            changes.append(f"status: {existing_match.status} -> {match.status}")

        if existing_match.venue != match.venue:
            changes.append(f"venue: {existing_match.venue} -> {match.venue}")

        if existing_match.referee1 != match.referee1:
            changes.append(f"referee1: {existing_match.referee1} -> {match.referee1}")

        if existing_match.referee2 != match.referee2:
            changes.append(f"referee2: {existing_match.referee2} -> {match.referee2}")

        # Si des changements existent, on met à jour le match
        if changes:
            return await update_match(session, match, changes)
        else:
            return existing_match
    else:
        # Si le match n'existe pas, on le crée
        new_match = await create_match(session, match)
        logger.info(f"Match {match.match_code} (pool_id: {match.pool_id}) créé avec succès.")
        return new_match

async def deactivate_matches(session: aiohttp.ClientSession, pool_id: int, scraped_match_codes: set) -> None:
    """
    Désactive les matchs qui existent en base mais n'ont pas été scrapés pour une pool spécifique.
    """
    # Récupérer tous les matchs actifs pour la pool donnée
    matches = await get_active_matches_by_pool_id(session, pool_id)
    if matches is None:
        return

    # Filtrer les matchs qui n'ont pas été scrapés
    matches_to_deactivate = [match for match in matches if match.match_code not in scraped_match_codes]

    # Désactiver ces matchs via des requêtes PUT
    for match in matches_to_deactivate:
        await deactivate_match(session, match.id)

async def log_started_matches() -> None:
    """
    Logue les matchs qui ont commencé.
    """
    current_time = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
    async with aiohttp.ClientSession() as session:
        started_matches = await get_started_matches(session, MatchStatus.UPCOMING, True, current_time)

        if started_matches:
            logger.info("Matchs en cours :")
            for match in started_matches:
                logger.info(f"Match {match.match_code} dans la ligue {match.league_code}: "
                            f"équipe A ({match.team_id_a}) vs équipe B ({match.team_id_b}) "
                            f"à {match.match_date} à {match.venue}")
        else:
            logger.info("Aucun match en cours trouvé.")