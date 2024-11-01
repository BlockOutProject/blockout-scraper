import asyncio
import aiohttp
from bs4 import BeautifulSoup
import logging
from models.pool import Pool, PoolDivisionCode
from services.pools_service import add_or_update_pool, deactivate_pools
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
    for a_tag in soup.find_all('a', href=lambda href: href and href.endswith('.htm')):
        href = a_tag['href']
        pool_name = a_tag.get_text(strip=True)
        pool_code = href.split('_')[-1].replace('.htm', '').upper()
        raw_season = extract_season_from_url(href)
        if not raw_season:
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
            "season": parse_season(raw_season),
            "league_name": league_name,
            "pool_name": pool_name,
            "division_code": PoolDivisionCode.NAT.value,
            "division_name": standardized["division"],
            "gender": standardized["gender"],
            "raw_division_name": raw_division_name
        }
        pool = Pool(**pool_data)
        
        new_pool = await add_or_update_pool(http_session, pool)
        if new_pool:

            task = handle_csv_download_and_parse(
                http_session, new_pool.id, new_pool.league_code, new_pool.pool_code, raw_season, folder
            )
            tasks.append(task)

    await asyncio.gather(*tasks)
    await deactivate_pools(http_session, league_code, scraped_pool_codes)
    logger.debug("Poules nationales ajoutées à la base de données.")
    delete_output_directory(folder)
