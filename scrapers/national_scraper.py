import asyncio
import aiohttp
from bs4 import BeautifulSoup
import logging
from errors_handler import handle_errors
from models.pool import PoolDivisionCode
from services.pools_service import add_or_update_pool, deactivate_pools
from session_manager import get_db_session
from utils import (
    create_output_directory,
    delete_output_directory,
    extract_season_from_url,
    handle_csv_download_and_parse,
    standardize_division_name,
    parse_season,
    extract_national_division,
    fetch
)

logger = logging.getLogger('blockout')

@handle_errors
async def scrape_national_pools(http_session):
    """
    Scrape les pools nationales et télécharge les CSV correspondants.

    Parameters:
    - http_session: La session aiohttp.
    """
    national_url = "http://www.ffvb.org/119-37-1-Championnats-Nationaux"
    folder = create_output_directory("National")
    logger.debug("Début du scraping des poules nationales.")

    html_content = await fetch(http_session, national_url)
    if not html_content:
        logger.error("Échec de la récupération du contenu HTML pour les pools nationales.")
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    tasks = []
    scraped_pool_codes = set()
    async with aiohttp.ClientSession() as session:
        for a_tag in soup.find_all('a', href=lambda href: href and href.endswith('.htm')):
            href = a_tag['href']
            pool_name = a_tag.get_text(strip=True)
            pool_code = href.split('_')[-1].replace('.htm', '').upper()
            season = extract_season_from_url(href)
            if not season:
                logger.warning(f"Aucune saison trouvée pour l'URL: {href}")
                continue
            raw_division_name = extract_national_division(pool_name)
            standardized = standardize_division_name(raw_division_name)
            league_code = "ABCCS"
            league_name = "NATIONAL"
            
            scraped_pool_codes.add(pool_code)
            
            pool_data = {
                "pool_code": pool_code,
                "league_code": league_code,
                "season": parse_season(season),
                "league_name": league_name,
                "pool_name": pool_name,
                "division_code": PoolDivisionCode.NAT.value,
                "division_name": standardized["division"],
                "gender": standardized["gender"],
                "raw_division_name": raw_division_name
            }
            
            new_pool = await add_or_update_pool(session, pool_data)
            if new_pool:
                pool_id = new_pool['id']

                task = handle_csv_download_and_parse(
                    http_session, pool_id, league_code, pool_code, season, folder
                )
                tasks.append(task)
        #deactivate_pools(pool_session, league_code, scraped_pool_codes)

    await asyncio.gather(*tasks)
    logger.debug("Poules nationales ajoutées à la base de données.")
    #delete_output_directory(folder)
