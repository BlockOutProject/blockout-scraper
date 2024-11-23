from typing import Optional, Set, List
import aiohttp
from datetime import datetime, timezone
from api.matches_api import create_match, deactivate_match, get_active_matches_by_pool_id, get_match_by_league_and_code, get_started_matches, update_match
from models.match import Match, MatchStatus
from utils.handlers.error_handler import handle_errors
from config.logger_config import logger

@handle_errors
async def add_or_update_match(session: aiohttp.ClientSession, match: Match, existing_match: Optional[Match]) -> Optional[Match]:
    """
    Vérifie l'existence d'un match et le met à jour ou le crée selon les besoins.
    """
    # Vérification des champs requis
    required_fields = ['league_code', 'match_code', 'pool_id', 'team_id_a', 'team_id_b', 'match_date']
    missing_fields = [field for field in required_fields if not getattr(match, field, None)]
    if missing_fields:
        raise ValueError(f"Les champs obligatoires suivants sont manquants : {', '.join(missing_fields)}.")
    
    if existing_match:
        # Cas où le match existe
        if existing_match.status == MatchStatus.UPCOMING:
            changes = []
            match.id = existing_match.id

            field_mappings = {
                "active": not existing_match.active,
                "team_id_a": existing_match.team_id_a != match.team_id_a,
                "team_id_b": existing_match.team_id_b != match.team_id_b,
                "match_date": match.league_code != 'AALNV' and existing_match.match_date.isoformat() != match.match_date.isoformat(),
                "set": existing_match.set != match.set,
                "score": existing_match.score != match.score,
                "status": existing_match.status != match.status,
                "venue": existing_match.venue != match.venue,
                "referee1": existing_match.referee1 != match.referee1,
                "referee2": existing_match.referee2 != match.referee2,
            }

            for field, has_changed in field_mappings.items():
                if has_changed:
                    changes.append(f"{field}: {getattr(existing_match, field)} -> {getattr(match, field)}")

            if changes:
                return await update_match(session, match, changes)
            return existing_match
        return existing_match

    # Cas où le match n'existe pas
    new_match = await create_match(session, match)
    logger.info(f"Match {match.match_code} (pool_id: {match.pool_id}) créé avec succès.")
    return new_match


@handle_errors
async def deactivate_matches(session: aiohttp.ClientSession, pool_id: int, scraped_match_codes: Set[str]) -> None:
    """
    Désactive les matchs qui existent en base mais n'ont pas été scrapés pour une pool spécifique.
    """
    matches = await get_active_matches_by_pool_id(session, pool_id)
    if not matches:
        return

    matches_to_deactivate = [match for match in matches if match.match_code not in scraped_match_codes]

    if not matches_to_deactivate:
        return

    for match in matches_to_deactivate:
        try:
            await deactivate_match(session, match.id)
            logger.info(f"Match {match.match_code} (ID: {match.id}) désactivé avec succès.")
        except Exception as e:
            logger.error(f"Erreur lors de la désactivation du match {match.match_code} (ID: {match.id}): {e}")


@handle_errors
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