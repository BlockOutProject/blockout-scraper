import asyncio
from bs4 import BeautifulSoup
import logging
import re
from errors_handler import handle_errors
from models.pool import PoolDivisionCode
from services.pools_service import add_or_update_pool, desactivate_pools
from session_manager import get_db_session
from utils import (
    create_output_directory,
    delete_output_directory,
    handle_csv_download_and_parse,
    standardize_division_name,
    parse_season,
    fetch
)

logger = logging.getLogger('blockout')

@handle_errors
async def scrape_pools_from_league(http_session, league_code, league_name, league_page_url, folder):
    """
    Scrape les informations des pools d'une ligue régionale et télécharge les CSV correspondants.

    Parameters:
    - http_session: La session aiohttp.
    - league_code (str): Le code de la ligue.
    - league_name (str): Le nom de la ligue.
    - league_page_url (str): L'URL de la page de la ligue.
    - folder (str): Le dossier de sauvegarde.
    - scraped_pool_codes (set): Un ensemble des pools codes scrapés.
    """
    scraped_pool_codes = set()
    
    if league_code not in ['LILO', 'LIMY', 'LIGY', 'LIGU', 'LIMART']:

        logger.debug(f"Scraping des pools pour la ligue: {league_name} ({league_code})")
        league_page_url = league_page_url.replace('https://', 'http://')

        html_content = await fetch(http_session, league_page_url)
        if not html_content:
            logger.error(f"Échec de la récupération du contenu HTML pour la ligue: {league_name}")
            return

        soup = BeautifulSoup(html_content, 'html.parser')
        pool_links = soup.select('ul#menu > li > ul > li > ul > li > a[href*="poule="]')
        tasks = []

        with get_db_session() as pool_session:
            for a_tag in pool_links:
                href = a_tag['href']
                pool_code_match = re.search(r'poule=([^&]+)', href)
                season_match = re.search(r'saison=([^&]+)', href)
                if not pool_code_match or not season_match:
                    logger.warning(f"Informations manquantes dans l'URL: {href}")
                    continue
                pool_code = pool_code_match.group(1)
                season = season_match.group(1)
                pool_name = a_tag.get_text(strip=True)
                raw_division_tag = a_tag.find_parent('ul').find_previous_sibling('a')
                raw_division_name = raw_division_tag.get_text(strip=True) if raw_division_tag else ""
                standardized = standardize_division_name(raw_division_name)

                scraped_pool_codes.add(pool_code)

                new_pool = add_or_update_pool(
                    pool_session,
                    pool_code=pool_code,
                    league_code=league_code,
                    season=parse_season(season),
                    league_name=league_name,
                    pool_name=pool_name,
                    division_code=PoolDivisionCode.REG,
                    division_name=standardized["division"],
                    gender=standardized["gender"],
                    raw_division_name=raw_division_name
                )
                pool_id = new_pool.id

                task = handle_csv_download_and_parse(
                    http_session, pool_id, league_code, pool_code, season, folder
                )
                tasks.append(task)

        await asyncio.gather(*tasks)
    with get_db_session() as pool_session:
        desactivate_pools(pool_session, league_code, scraped_pool_codes)
    logger.debug(f"Pools pour la ligue {league_name} ajoutées à la base de données.")


@handle_errors
async def scrape_regional_pools(http_session):
    """
    Scrape tous les pools régionaux et leurs ligues associées.

    Parameters:
    - http_session: La session aiohttp.
    """
    regional_url = "http://www.ffvb.org/120-37-1-Championnats-Regionaux"
    folder = create_output_directory("Regional")
    scraped_league_codes = set()
    logger.debug("Début du scraping des poules régionales.")

    html_content = await fetch(http_session, regional_url)
    if not html_content:
        logger.error("Échec de la récupération du contenu HTML pour les pools régionales.")
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    league_tables = soup.find_all("table", class_=["tableau_bleu", "tableau_rouge", "tableau_violet"])
    tasks = []

    for table in league_tables:
        league_name_tag = table.find('td', style="text-align: center;")
        if not league_name_tag:
            continue
        league_name = league_name_tag.get_text(strip=True)
        a_tag = table.find('a', href=lambda href: href and 'codent=' in href)
        if a_tag:
            league_code_match = re.search(r'codent=([^&]+)', a_tag['href'])
            if not league_code_match:
                logger.warning(f"Code de ligue manquant dans l'URL: {a_tag['href']}")
                continue
            league_code = league_code_match.group(1)
            league_page_url = a_tag['href']
            scraped_league_codes.add(league_code)
            
            task = scrape_pools_from_league(
                http_session, league_code, league_name, league_page_url, folder
            )
            tasks.append(task)

    await asyncio.gather(*tasks)

    logger.debug("Poules régionales ajoutées à la base de données.")
    delete_output_directory(folder)