# regional_scraper.py
import asyncio
from bs4 import BeautifulSoup
import logging
import re
from errors_handler import handle_errors
from services.pools_service import add_pool
from session_manager import get_db_session
from utils import (
    create_output_directory,
    handle_csv_download_and_parse,
    standardize_division,
    parse_season,
    fetch
)

# Importer le logger configuré
logger = logging.getLogger('myvolley')

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
    """
    logger.info(f"Scraping des pools pour la ligue: {league_name} ({league_code})")
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
            raw_division = raw_division_tag.get_text(strip=True) if raw_division_tag else ""
            standardized = standardize_division(raw_division)

            new_pool = add_pool(
                pool_session,
                pool_code=pool_code,
                league_code=league_code,
                season=parse_season(season),
                league_name=league_name,
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

        logger.info(f"Pools pour la ligue {league_name} ajoutées à la base de données.")

    await asyncio.gather(*tasks)
    logger.info(f"Scraping des pools pour la ligue {league_name} terminé.")

@handle_errors
async def scrape_regional_pools(http_session):
    """
    Scrape tous les pools régionaux et leurs ligues associées.

    Parameters:
    - http_session: La session aiohttp.
    """
    regional_url = "http://www.ffvb.org/120-37-1-Championnats-Regionaux"
    folder = create_output_directory("Regional")
    logger.info("Début du scraping des pools régionales.")

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
            task = scrape_pools_from_league(
                http_session, league_code, league_name, league_page_url, folder
            )
            tasks.append(task)

    await asyncio.gather(*tasks)
    logger.info("Scraping des pools régionales terminé.")