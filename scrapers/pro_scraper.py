# pro_scraper.py
import asyncio
import logging

import aiohttp
from errors_handler import handle_errors
from models.pool import PoolDivisionCode
from services.pools_service import add_or_update_pool
from utils import (
    create_output_directory,
    delete_output_directory,
    handle_csv_download_and_parse,
    parse_season
)

logger = logging.getLogger('blockout')

@handle_errors
async def scrape_pro_pools(http_session):
    """
    Scrape les pools professionnelles et télécharge les CSV correspondants.

    Parameters:
    - http_session: La session aiohttp.
    """
    folder = create_output_directory("Pro")
    season = "2024/2025"  # Mettez à jour la saison si nécessaire
    league_code = "AALNV"
    league_name = "PRO"

    pools = [
        {"code": "MSL", "pool_name": "Marmara SpikeLigue", "division_name": "Marmara SpikeLigue", "gender": "M"},
        {"code": "LBM", "pool_name": "Ligue B Masculine", "division_name": "Ligue B Masculine", "gender": "M"},
        {"code": "LAF", "pool_name": "Saforelle Power 6", "division_name": "Saforelle Power 6", "gender": "F"},
    ]

    tasks = []

    async with aiohttp.ClientSession() as session:
        logger.debug("Début du scraping des poules professionnelles.")
        
        for pool in pools:
            pool_data = {
                "pool_code": pool['code'],
                "league_code": league_code,
                "season": parse_season(season),
                "league_name": league_name,
                "pool_name": pool['pool_name'],
                "division_code": PoolDivisionCode.PRO.value,
                "division_name": pool['division_name'],
                "gender": pool['gender']
            }

            new_pool = await add_or_update_pool(session, pool_data)
            if new_pool:
                pool_id = new_pool['id']

                # Gestion du téléchargement et parsing du CSV
                task = handle_csv_download_and_parse(
                    http_session, pool_id, league_code, pool['code'], season, folder
                )
                tasks.append(task)

        await asyncio.gather(*tasks)

    logger.debug("Poules professionnelles ajoutées à la base de données via API.")
    delete_output_directory(folder)