import asyncio
import logging
from models.pool import Pool, PoolDivisionCode
from scrapers.lnv_scraper import add_match_live_code, parse_and_update_matches
from services.pools_service import add_or_update_pool
from utils.file_utils import create_output_directory, delete_output_directory
from utils.scraper_logic import handle_csv_download_and_parse
from utils.utils import parse_season


logger = logging.getLogger('blockout')

async def scrape_pro_pools(http_session):
    """
    Scrape les pools professionnelles et télécharge les CSV correspondants.

    Parameters:
    - http_session: La session aiohttp.
    """
    folder = create_output_directory("Pro")
    raw_season = "2024/2025"  # Mettez à jour la saison si nécessaire
    league_code = "AALNV"
    league_name = "PRO"

    pools_json = [
        {"code": "MSL", "pool_name": "Marmara SpikeLigue", "division_name": "Marmara SpikeLigue", "gender": "M", "lnv_url": "http://lnv-web.dataproject.com/CompetitionMatches.aspx?ID=115", "lnv_xml_url": "https://www.lnv.fr/xml/calendrier-LAM.xml"},
        {"code": "LBM", "pool_name": "Ligue B Masculine", "division_name": "Ligue B Masculine", "gender": "M", "lnv_url": "http://lnv-web.dataproject.com/CompetitionMatches.aspx?ID=116", "lnv_xml_url": "https://www.lnv.fr/xml/calendrier-LBM.xml"},
        {"code": "LAF", "pool_name": "Saforelle Power 6", "division_name": "Saforelle Power 6", "gender": "F", "lnv_url": "http://lnv-web.dataproject.com/CompetitionMatches.aspx?ID=113", "lnv_xml_url": "https://www.lnv.fr/xml/calendrier-LAF.xml"},
    ]

    tasks = []

    logger.debug("Début du scraping des poules professionnelles.")
    
    for pool_json in pools_json:
        pool_data = {
            "pool_code": pool_json['code'],
            "league_code": league_code,
            "season": parse_season(raw_season),
            "league_name": league_name,
            "pool_name": pool_json['pool_name'],
            "division_code": PoolDivisionCode.PRO.value,
            "division_name": pool_json['division_name'],
            "gender": pool_json['gender']
        }
        pool = Pool(**pool_data)

        new_pool = await add_or_update_pool(http_session, pool)
        if new_pool:

            async def execute_task_chain(pool_id, pool_code, season, gender, folder, lnv_url, lnv_xml_url):
                await handle_csv_download_and_parse(http_session, pool_id, league_code, pool_code, season, folder)
                await parse_and_update_matches(http_session, lnv_xml_url, pool_id)
                await add_match_live_code(http_session, lnv_url, pool_id, gender)

            tasks.append(execute_task_chain(new_pool.id, new_pool.pool_code, raw_season, new_pool.gender, folder, pool_json['lnv_url'], pool_json['lnv_xml_url']))

    await asyncio.gather(*tasks)

    logger.debug("Poules professionnelles ajoutées à la base de données via API.")
    delete_output_directory(folder)