import asyncio
import logging
from utils.downloader import download_csv
from models.match import Match, MatchStatus
from models.team import Team
from services.matchs_service import add_or_update_match, deactivate_matches
from services.teams_service import add_or_update_team, deactivate_teams
from utils.date_utils import parse_date
from utils.file_utils import parse_csv
from utils.handlers.error_handler import handle_errors

logger = logging.getLogger('blockout')

@handle_errors
async def handle_csv_download_and_parse(
    http_session,
    pool_id: int,
    league_code: str,
    pool_code: str,
    season: str,
    folder: str
) -> None:
    """
    Gère le téléchargement et le parsing du CSV de manière asynchrone.
    """
    
    logger.debug(f"Téléchargement du CSV pour Pool ID: {pool_id}, League Code: {league_code}, Pool Code: {pool_code}")
    csv_path = await download_csv(http_session, league_code, pool_code, season, folder)

    if not csv_path:
        raise Exception(f"Échec du téléchargement du CSV pour Pool Code: {pool_code}")

    logger.debug(f"CSV téléchargé avec succès: {csv_path}")
    await parse_and_add_matches_from_csv(http_session, pool_id, csv_path)

@handle_errors
async def parse_and_add_matches_from_csv(http_session, pool_id: int, csv_path: str) -> None:
    """
    Parse le fichier CSV et ajoute les matchs et les équipes via des appels API REST.
    """

    logger.debug(f"Parsing et ajout des matchs depuis le CSV: {csv_path}")
    scraped_team_names = set()
    scraped_match_codes = set()

    for data in parse_csv(csv_path):
        club_a_id = data['club_a_id']
        club_b_id = data['club_b_id']

        if (club_a_id and club_b_id):
            match_datetime = parse_date(data['match_date'], data['match_time'])
            if not match_datetime:
                logger.warning(f"Date invalide pour le match {data['match_code']}. Match ignoré.")
                continue 

            # Ajouter ou mettre à jour les équipes
            team_a_data = {
                "team_name": data['team_a_name'],
                "club_id": club_a_id,
                "pool_id": pool_id
            }
            team_b_data = {
                "team_name": data['team_b_name'],
                "club_id": club_b_id,
                "pool_id": pool_id
            }

            team_a = Team(**team_a_data)
            team_b = Team(**team_b_data)

            new_team_a = await add_or_update_team(http_session, team_a)
            new_team_b = await add_or_update_team(http_session, team_b)

            if new_team_a and new_team_b:
                scraped_team_names.add(new_team_a.team_name)
                scraped_team_names.add(new_team_b.team_name)

                # Ajouter ou mettre à jour le match
                match_data = {
                    "match_code": data['match_code'],
                    "league_code": data['league_code'],
                    "pool_id": pool_id,
                    "team_id_a": new_team_a.id,
                    "team_id_b": new_team_b.id,
                    "match_date": match_datetime,
                    "set": None if not data['set'] else data['set'].replace('/', '-'),
                    "score": None if not data['score'] else data['score'],
                    "status": MatchStatus.FINISHED if data['set'] and data['score'] else MatchStatus.UPCOMING,
                    "venue": None if not data['venue'] else data['venue'],
                    "referee1": None if not data['referee1'] else data['referee1'],
                    "referee2": None if not data['referee2'] else data['referee2']
                }
                match = Match(**match_data)
                new_match = await add_or_update_match(http_session, match)
                scraped_match_codes.add(new_match.match_code)


    await asyncio.gather(
        deactivate_teams(http_session, pool_id, scraped_team_names),
        deactivate_matches(http_session, pool_id, scraped_match_codes)
    )
    logger.debug(f"Terminé l'ajout des matchs depuis le CSV: {csv_path}")

        
