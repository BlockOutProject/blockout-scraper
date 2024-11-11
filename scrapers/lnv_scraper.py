from dataclasses import replace
from datetime import datetime
import logging
from bs4 import BeautifulSoup
import re
from api.matchs_api import get_match_by_pool_teams_date, update_match, get_active_matches_by_pool_id
from api.teams_api import get_team_by_pool_and_name
from models.match import Match, MatchStatus
from typing import Optional, Tuple
import xml.etree.ElementTree as ET

from utils.scraper_logic import fetch
from utils.team_utils import get_full_team_name

logger = logging.getLogger('blockout')

async def parse_and_update_matches(http_session, xml_url, pool_id):
    """
    Parse le flux XML des matchs et met à jour les informations des matchs dans la base.
    """
    xml_content = await fetch(http_session, xml_url)
    if not xml_content:
        logger.error("Erreur lors de la récupération du flux XML.")
        return

    root = ET.fromstring(xml_content)  # Décoder le contenu XML
    existing_matches = await get_active_matches_by_pool_id(http_session, pool_id)
    for match in root.findall(".//Match"):
        await process_xml_match(match, existing_matches, http_session)

async def process_xml_match(match, existing_matches : Optional[list[Match]], http_session):
    code_match = match.find("CodeMatch").text
    match_date = match.find("Date").text + " " + match.find("Heure").text
    set = match.find("Score").text # Set fait reference au champ csv, attention à la confusion avec Score

    # Conversion de la date et de l'heure en format datetime
    match_datetime = datetime.strptime(match_date, "%d-%m-%Y %H:%M:%S")
    existing_match = next((match for match in existing_matches if match.match_code == code_match), None)

    if existing_match:
        updated_match = prepare_updated_match(existing_match, match_datetime, set)
        await apply_match_updates(http_session, existing_match, updated_match)

async def apply_match_updates(http_session, existing_match: Match, updated_match: Match):
    changes = []
    if existing_match.match_date != updated_match.match_date:
        changes.append(f"match_date: {existing_match.match_date} -> {updated_match.match_date}")
    if existing_match.set != updated_match.set:
        changes.append(f"set: '{existing_match.set}' -> '{updated_match.set}'")
    if changes:
        await update_match(http_session, updated_match, changes)

def prepare_updated_match(existing_match: Match, match_datetime, set) -> Match:
    updated_match = replace(existing_match)
    updated_match.match_date = match_datetime.isoformat()
    if set != "0-0":
        updated_match.set = set
        if '3' in set:
            updated_match.status = MatchStatus.FINISHED.value
    return updated_match

async def extract_main_id(soup: BeautifulSoup) -> Optional[str]:
    span = soup.find("span", id=re.compile(r"Content_Main_(\d+)_userControl_lbl_title"))
    if span:
        match = re.search(r"Content_Main_(\d+)_userControl_lbl_title", span["id"])
        return match.group(1) if match else None
    return None

async def add_match_live_code(http_session, url, pool_id, gender):
    html_content = await fetch(http_session, url)
    if not html_content:
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    main_id = await extract_main_id(soup)
    if not main_id:
        logger.error("Impossible de trouver l'identifiant principal.")
        return
    logger.debug(f"Identifiant principal trouvé: {main_id}")

    await process_all_days(soup, main_id, http_session, pool_id, gender)

async def process_all_days(soup, main_id: str, http_session, pool_id: int, gender: str):
    total_days = 0
    while True:
        day_block = soup.find(id=f"ctl00_Content_Main_{main_id}_userControl_RADLIST_Legs_ctrl{total_days}_RPL_Leg")
        if not day_block:
            break
        await process_matches_in_day(soup, main_id, total_days, http_session, pool_id, gender)
        total_days += 2

async def process_matches_in_day(soup, main_id: str, total_days: int, http_session, pool_id: int, gender: str):
    match_count = 0
    while True:
        match_block = soup.find(id=f"ctl00_Content_Main_{main_id}_userControl_RADLIST_Legs_ctrl{total_days}_RADLIST_Matches_ctrl{match_count}_RPL_Match")
        if not match_block:
            break
        await process_match_block(match_block, http_session, pool_id, gender)
        match_count += 2

async def process_match_block(match_block, http_session, pool_id: int, gender: str):    
    mID = extract_match_id(match_block)
    home_team_name, guest_team_name = extract_teams(match_block)
    home_team_full = get_full_team_name(home_team_name, gender)
    guest_team_full = get_full_team_name(guest_team_name, gender)

    if not home_team_full:
        logger.error(f"Nom d'équipe domicile non trouvé dans les alias: {home_team_name}")
    if not guest_team_full:
        logger.error(f"Nom d'équipe visiteur non trouvé dans les alias: {guest_team_name}")

    date_time = match_block.find("span", id=re.compile("LB_DataOra"))
    if date_time:
        match_date = date_time.get_text(strip=True)
        parsed_match_date = datetime.strptime(match_date, "%d/%m/%Y - %H:%M")

        if home_team_full and guest_team_full:
            await update_match_details(http_session, pool_id, home_team_full, guest_team_full, parsed_match_date, mID)

def extract_match_id(match_block) -> str:
    onclick_attr = match_block.find("div", onclick=True)
    mID_match = re.search(r"mID=(\d+)", onclick_attr["onclick"]) if onclick_attr else None
    return mID_match.group(1) if mID_match else None

def extract_teams(match_block) -> Tuple[str, str]:
    team_home = match_block.find("span", id=re.compile("Label2|Label6"))
    team_guest = match_block.find("span", id=re.compile("Label4|Label7"))
    home_team_name = team_home.get_text(strip=True) if team_home else None
    guest_team_name = team_guest.get_text(strip=True) if team_guest else None
    return home_team_name, guest_team_name

async def update_match_details(http_session, pool_id: int, home_team_full: str, guest_team_full: str, match_date: datetime, mID: str):
    team_a = await get_team_by_pool_and_name(http_session, pool_id, home_team_full)
    team_b = await get_team_by_pool_and_name(http_session, pool_id, guest_team_full)

    if team_a and team_b:
        existing_match = await get_match_by_pool_teams_date(http_session, pool_id, team_a.id, team_b.id, match_date)
        if existing_match:
            updated_match = replace(existing_match)
            updated_match.live_code = int(mID)
            if existing_match.live_code != updated_match.live_code:
                changes = [f"live_code: {existing_match.live_code} -> {updated_match.live_code}"]
                await update_match(http_session, updated_match, changes)