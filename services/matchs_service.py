from typing import Optional
import aiohttp
from datetime import datetime, timezone
from api.matchs_api import create_match, deactivate_match, get_active_matches_by_pool_id, get_match_by_league_and_code, get_started_matches, update_match
import logging
from models.match import Match, MatchStatus
from utils.handlers.function_name_handler import log_function_name

logger = logging.getLogger('blockout')

@log_function_name
async def add_or_update_match(session: aiohttp.ClientSession, match: Match) -> Optional[Match]:
    """
    Vérifie l'existence d'un match et le met à jour ou le crée selon les besoins.
    """
    try:
        # Vérification des champs requis
        required_fields = ['league_code', 'match_code', 'pool_id', 'team_id_a', 'team_id_b', 'match_date']
        missing_fields = [field for field in required_fields if not getattr(match, field, None)]
        if missing_fields:
            raise ValueError(f"Les champs obligatoires suivants sont manquants : {', '.join(missing_fields)}.")

        # Convertir datetime en ISO 8601 si nécessaire
        if match.match_date and isinstance(match.match_date, datetime):
            match.match_date = match.match_date.isoformat()

        # Vérification de l'existence du match
        existing_match = await get_match_by_league_and_code(session, match.league_code, match.match_code)

        if existing_match:
            # Cas où le match existe
            if existing_match.status == MatchStatus.UPCOMING.value:
                changes = []
                match.id = existing_match.id

                # Comparaison des champs pour détecter les changements
                field_mappings = {
                    "active": not existing_match.active,
                    "team_id_a": existing_match.team_id_a != match.team_id_a,
                    "team_id_b": existing_match.team_id_b != match.team_id_b,
                    "match_date": match.league_code != 'AALNV' and existing_match.match_date != match.match_date,
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
                    logger.info(f"Changements détectés pour le match {existing_match.match_code}: {', '.join(changes)}")
                    return await update_match(session, match, changes)
                else:
                    return existing_match
            else:
                return existing_match
        else:
            # Cas où le match n'existe pas
            new_match = await create_match(session, match)
            logger.info(f"Match {match.match_code} (pool_id: {match.pool_id}) créé avec succès.")
            return new_match

    except ValueError as e:
        logger.error(f"Erreur de validation lors de l'ajout ou de la mise à jour du match : {e}")
        raise

    except Exception as e:
        logger.exception(f"Erreur inattendue lors du traitement du match {match.match_code}: {e}")
        raise

    
@log_function_name
async def deactivate_matches(session: aiohttp.ClientSession, pool_id: int, scraped_match_codes: set) -> None:
    """
    Désactive les matchs qui existent en base mais n'ont pas été scrapés pour une pool spécifique.
    """
    try:
        # Récupérer tous les matchs actifs pour la pool donnée
        matches = await get_active_matches_by_pool_id(session, pool_id)
        if not matches:
            return

        # Filtrer les matchs qui n'ont pas été scrapés
        matches_to_deactivate = [match for match in matches if match.match_code not in scraped_match_codes]

        if not matches_to_deactivate:
            return

        # Désactiver les matchs
        for match in matches_to_deactivate:
            await deactivate_match(session, match.id)

    except Exception as e:
        logger.exception(f"Erreur inattendue lors de la désactivation des matchs pour pool_id {pool_id}: {e}")
        raise
    
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