# national_scraper.py
import asyncio
from bs4 import BeautifulSoup
import logging
from errors_handler import handle_errors
from services.pools_service import add_pool
from session_manager import get_db_session
from utils import (
    create_output_directory,
    extract_season_from_url,
    handle_csv_download_and_parse,
    standardize_division,
    parse_season,
    extract_national_division,
    fetch
)

# Importer le logger configuré
logger = logging.getLogger('myvolley')

@handle_errors
async def scrape_national_pools(http_session):
    """
    Scrape les pools nationales et télécharge les CSV correspondants.

    Parameters:
    - http_session: La session aiohttp.
    """
    national_url = "http://www.ffvb.org/119-37-1-Championnats-Nationaux"
    folder = create_output_directory("National")
    logger.info("Début du scraping des pools nationales.")

    html_content = await fetch(http_session, national_url)
    if not html_content:
        logger.error("Échec de la récupération du contenu HTML pour les pools nationales.")
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    tasks = []

    with get_db_session() as pool_session:
        for a_tag in soup.find_all('a', href=lambda href: href and href.endswith('.htm')):
            href = a_tag['href']
            pool_name = a_tag.get_text(strip=True)
            pool_code = href.split('_')[-1].replace('.htm', '').upper()
            season = extract_season_from_url(href)
            if not season:
                logger.warning(f"Aucune saison trouvée pour l'URL: {href}")
                continue
            raw_division = extract_national_division(pool_name)
            standardized = standardize_division(raw_division)
            league_code = "ABCCS"

            new_pool = add_pool(
                pool_session,
                pool_code=pool_code,
                league_code=league_code,
                season=parse_season(season),
                league_name="NATIONAL",
                pool_name=pool_name,
                division=standardized["division"],
                gender=standardized["gender"],
                raw_division=raw_division
            )
            pool_id = new_pool.id

            task = handle_csv_download_and_parse(
                http_session, pool_id, league_code, pool_code, season, folder
            )
            tasks.append(task)

        logger.info("Pools nationales ajoutées à la base de données.")

    await asyncio.gather(*tasks)
    logger.info("Scraping des pools nationales terminé.")