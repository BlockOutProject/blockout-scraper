import asyncio
from dataclasses import replace
from datetime import datetime
import re
from typing import Optional, Tuple
from bs4 import BeautifulSoup
from api.matches_api import get_active_matches_by_pool_id, get_match_by_pool_teams_date, update_match
from api.teams_api import get_team_by_pool_and_name
from models.match import Match, MatchStatus
from models.pool import Pool, PoolDivisionCode, PoolGender
from models.scraper import Scraper
from services.pools_service import add_or_update_pool
from utils.file_utils import create_output_directory, delete_output_directory
from utils.scraper_logic import handle_csv_download_and_parse
from utils.team_utils import get_full_team_name
from utils.utils import parse_season
import xml.etree.ElementTree as ET


class ProScraper(Scraper):
    def __init__(self, session):
        super().__init__(session)
        self.folder = create_output_directory("Pro")
        self.raw_season = "2024/2025" 
        self.league_code = "AALNV"
        self.league_name = "PRO"
        self.pools_json = [
            {"code": "MSL", "pool_name": "Marmara SpikeLigue", "division_name": "Marmara SpikeLigue", "gender": "M", "lnv_url": "http://lnv-web.dataproject.com/CompetitionMatches.aspx?ID=115", "lnv_xml_url": "https://www.lnv.fr/xml/calendrier-LAM.xml"},
            {"code": "LBM", "pool_name": "Ligue B Masculine", "division_name": "Ligue B Masculine", "gender": "M", "lnv_url": "http://lnv-web.dataproject.com/CompetitionMatches.aspx?ID=116", "lnv_xml_url": "https://www.lnv.fr/xml/calendrier-LBM.xml"},
            {"code": "LAF", "pool_name": "Saforelle Power 6", "division_name": "Saforelle Power 6", "gender": "F", "lnv_url": "http://lnv-web.dataproject.com/CompetitionMatches.aspx?ID=113", "lnv_xml_url": "https://www.lnv.fr/xml/calendrier-LAF.xml"},
        ]


    async def scrape(self):
        if self.session is None:
            raise ValueError("La session aiohttp est non initialisée ou fermée.")

        tasks = []
        self.logger.debug("Début du scraping des poules professionnelles.")

        try:
            for pool_json in self.pools_json:
                try:
                    pool_data = {
                        "pool_code": pool_json['code'],
                        "league_code": self.league_code,
                        "season": parse_season(self.raw_season),
                        "league_name": self.league_name,
                        "pool_name": pool_json['pool_name'],
                        "division_code": PoolDivisionCode.PRO,
                        "division_name": pool_json['division_name'],
                        "gender": pool_json['gender']
                    }
                    pool = Pool(**pool_data)

                    new_pool = await add_or_update_pool(self.session, pool)
                    if new_pool:
                        tasks.append(self.execute_task_chain(
                            new_pool.id, new_pool.pool_code, self.raw_season,
                            new_pool.gender, self.folder, pool_json['lnv_url'], pool_json['lnv_xml_url']
                        ))
                except Exception as e:
                    self.logger.error(f"Erreur lors du traitement de la pool {pool_json['pool_name']}: {e}")

            # Exécute les tâches asynchrones (ex. téléchargement de CSV, parsing XML)
            await asyncio.gather(*tasks)

        except Exception as e:
            self.logger.error(f"Erreur critique lors du scraping des poules professionnelles : {e}")
        finally:
            # Nettoyer le dossier, même en cas d'échec
            delete_output_directory(self.folder)
            self.logger.debug("Fin du scraping des poules professionnelles.")
            
            
    async def execute_task_chain(self, pool_id, pool_code, season, gender, folder, lnv_url, lnv_xml_url):
        await handle_csv_download_and_parse(self.session, pool_id, self.league_code, pool_code, season, folder)
        await self.parse_and_update_matches(lnv_xml_url, pool_id)
        await self.add_match_live_code(lnv_url, pool_id, gender)
        
        
    async def parse_and_update_matches(self, xml_url, pool_id):
        """
        Parse le flux XML des matchs et met à jour les informations des matchs dans la base.
        """
        xml_content = await self.fetch(xml_url)
        if not xml_content:
            self.logger.error("Erreur lors de la récupération du flux XML.")
            return

        root = ET.fromstring(xml_content)  # Décoder le contenu XML
        existing_matches = await get_active_matches_by_pool_id(self.session, pool_id)
        for match in root.findall(".//Match"):
            await self.process_xml_match(match, existing_matches)


    async def process_xml_match(self, match, existing_matches : Optional[list[Match]]):
        code_match = match.find("CodeMatch").text
        match_date = match.find("Date").text + " " + match.find("Heure").text
        set = match.find("Score").text # Set fait reference au champ csv, attention à la confusion avec Score

        # Conversion de la date et de l'heure en format datetime
        match_datetime = datetime.strptime(match_date, "%d-%m-%Y %H:%M:%S")
        existing_match = next((match for match in existing_matches if match.match_code == code_match), None)

        if existing_match:
            updated_match = self.prepare_updated_match(existing_match, match_datetime, set)
            await self.apply_match_updates(existing_match, updated_match)


    async def apply_match_updates(self, existing_match: Match, updated_match: Match):
        changes = []
        formated_existing_date = existing_match.match_date.isoformat()
        formated_updated_date = updated_match.match_date.isoformat()
        if formated_existing_date != formated_updated_date:
            changes.append(f"match_date: {formated_existing_date} -> {formated_updated_date}")
        if existing_match.set != updated_match.set:
            changes.append(f"set: '{existing_match.set}' -> '{updated_match.set}'")
        if changes:
            await update_match(self.session, updated_match, changes)


    def prepare_updated_match(self, existing_match: Match, match_datetime: datetime, set: set) -> Match:
        updated_match = replace(existing_match)
        updated_match.match_date = match_datetime
        if set != "0-0":
            updated_match.set = set
            if '3' in set:
                updated_match.status = MatchStatus.FINISHED
        return updated_match


    async def extract_main_id(self, soup: BeautifulSoup) -> Optional[str]:
        span = soup.find("span", id=re.compile(r"Content_Main_(\d+)_userControl_lbl_title"))
        if span:
            match = re.search(r"Content_Main_(\d+)_userControl_lbl_title", span["id"])
            return match.group(1) if match else None
        return None


    async def add_match_live_code(self, url, pool_id, gender):
        html_content = await self.fetch(url)
        if not html_content:
            return

        soup = BeautifulSoup(html_content, 'html.parser')
        main_id = await self.extract_main_id(soup)
        if not main_id:
            self.logger.error("Impossible de trouver l'identifiant principal.")
            return
        self.logger.debug(f"Identifiant principal trouvé: {main_id}")

        await self.process_all_days(soup, main_id, pool_id, gender)


    async def process_all_days(self, soup: BeautifulSoup, main_id: str, pool_id: int, gender: str):
        total_days = 0
        while True:
            day_block = soup.find(id=f"ctl00_Content_Main_{main_id}_userControl_RADLIST_Legs_ctrl{total_days}_RPL_Leg")
            if not day_block:
                break
            await self.process_matches_in_day(soup, main_id, total_days, pool_id, gender)
            total_days += 2


    async def process_matches_in_day(self, soup: BeautifulSoup, main_id: str, total_days: int, pool_id: int, gender: str):
        match_count = 0
        while True:
            match_block = soup.find(id=f"ctl00_Content_Main_{main_id}_userControl_RADLIST_Legs_ctrl{total_days}_RADLIST_Matches_ctrl{match_count}_RPL_Match")
            if not match_block:
                break
            await self.process_match_block(match_block, pool_id, gender)
            match_count += 2


    async def process_match_block(self, match_block, pool_id: int, gender: str):    
        mID = self.extract_match_id(match_block)
        home_team_name, guest_team_name = self.extract_teams(match_block)
        home_team_full = get_full_team_name(home_team_name, gender)
        guest_team_full = get_full_team_name(guest_team_name, gender)

        if not home_team_full:
            self.logger.error(f"Nom d'équipe domicile non trouvé dans les alias: {home_team_name}")
        if not guest_team_full:
            self.logger.error(f"Nom d'équipe visiteur non trouvé dans les alias: {guest_team_name}")

        date_time = match_block.find("span", id=re.compile("LB_DataOra"))
        if date_time:
            match_date = date_time.get_text(strip=True)
            parsed_match_date = datetime.strptime(match_date, "%d/%m/%Y - %H:%M")

            if home_team_full and guest_team_full:
                await self.update_match_details(pool_id, home_team_full, guest_team_full, parsed_match_date, mID)


    def extract_match_id(self, match_block) -> str:
        onclick_attr = match_block.find("div", onclick=True)
        mID_match = re.search(r"mID=(\d+)", onclick_attr["onclick"]) if onclick_attr else None
        return mID_match.group(1) if mID_match else None


    def extract_teams(self, match_block) -> Tuple[str, str]:
        team_home = match_block.find("span", id=re.compile("Label2|Label6"))
        team_guest = match_block.find("span", id=re.compile("Label4|Label7"))
        home_team_name = team_home.get_text(strip=True) if team_home else None
        guest_team_name = team_guest.get_text(strip=True) if team_guest else None
        return home_team_name, guest_team_name


    async def update_match_details(self, pool_id: int, home_team_full: str, guest_team_full: str, match_date: datetime, mID: str):
        team_a = await get_team_by_pool_and_name(self.session, pool_id, home_team_full)
        team_b = await get_team_by_pool_and_name(self.session, pool_id, guest_team_full)

        if team_a and team_b:
            existing_match = await get_match_by_pool_teams_date(self.session, pool_id, team_a.id, team_b.id, match_date)
            if existing_match:
                updated_match = replace(existing_match)
                updated_match.live_code = int(mID)
                if existing_match.live_code != updated_match.live_code:
                    changes = [f"live_code: {existing_match.live_code} -> {updated_match.live_code}"]
                    await update_match(self.session, updated_match, changes)