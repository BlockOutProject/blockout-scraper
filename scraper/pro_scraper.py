# pro_scraper.py
import asyncio
import logging
from errors_handler import handle_errors
from services.pools_service import add_pool
from session_manager import get_db_session
from utils import (
    create_output_directory,
    handle_csv_download_and_parse,
    parse_season
)

# Importer le logger configuré
logger = logging.getLogger('myvolley')

@handle_errors
async def scrape_pro_pools(http_session):
    """
    Scrape les pools professionnelles et télécharge les CSV correspondants.

    Parameters:
    - http_session: La session aiohttp.
    """
    folder = create_output_directory("Pro")
    season = "2023/2024"  # Mettez à jour la saison si nécessaire
    league_code = "AALNV"
    league_name = "PRO"

    pools = [
        {"code": "MSL", "pool_name": "Marmara SpikeLigue", "division": "Marmara SpikeLigue", "gender": "M"},
        {"code": "LBM", "pool_name": "Ligue B Masculine", "division": "Ligue B Masculine", "gender": "M"},
        {"code": "LAF", "pool_name": "Saforelle Power 6", "division": "Saforelle Power 6", "gender": "F"},
    ]

    tasks = []

    with get_db_session() as db_session:
        for pool in pools:
            new_pool = add_pool(
                db_session,
                pool_code=pool['code'],
                league_code=league_code,
                season=parse_season(season),
                league_name=league_name,
                pool_name=pool['pool_name'],
                division=pool['division'],
                gender=pool['gender']
            )
            pool_id = new_pool.id

            task = handle_csv_download_and_parse(
                http_session, pool_id, league_code, pool['code'], season, folder
            )
            tasks.append(task)

        logger.info("Pools professionnelles ajoutées à la base de données.")

    await asyncio.gather(*tasks)
    logger.info("Scraping des pools professionnelles terminé.")