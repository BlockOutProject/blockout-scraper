import asyncio
import re
from bs4 import BeautifulSoup
from models.pool import Pool, PoolDivisionCode
from models.scraper import Scraper
from services.pools_service import add_or_update_pool, deactivate_pools
from utils.file_utils import create_output_directory, delete_output_directory
from utils.scraper_logic import handle_csv_download_and_parse
from utils.utils import parse_season, standardize_division_name


class RegionalScraper(Scraper):
    def __init__(self, session):
        super().__init__(session)
        self.regional_url = "http://www.ffvb.org/120-37-1-Championnats-Regionaux"
        self.folder = create_output_directory("Regional")


    async def scrape(self):
        self.logger.debug("Début du scraping des poules régionales.")
        scraped_league_codes = set()

        try:
            html_content = await self.fetch(self.regional_url)
            if not html_content:
                self.logger.error("Échec de la récupération du contenu HTML pour les pools régionales.")
                return

            soup = BeautifulSoup(html_content, 'html.parser')
            league_tables = soup.find_all("table", class_=["tableau_bleu", "tableau_rouge", "tableau_violet"])
            tasks = []

            for table in league_tables:
                try:
                    league_name_tag = table.find('td', style="text-align: center;")
                    if not league_name_tag:
                        continue
                    league_name = league_name_tag.get_text(strip=True)
                    a_tag = table.find('a', href=lambda href: href and 'codent=' in href)
                    if a_tag:
                        league_code_match = re.search(r'codent=([^&]+)', a_tag['href'])
                        if not league_code_match:
                            self.logger.warning(f"Code de ligue manquant dans l'URL: {a_tag['href']}")
                            continue
                        league_code = league_code_match.group(1)
                        league_page_url = a_tag['href']
                        scraped_league_codes.add(league_code)

                        task = self.scrape_pools_from_league(
                            league_code, league_name, league_page_url
                        )
                        tasks.append(task)
                except Exception as e:
                    self.logger.error(f"Erreur lors du traitement d'une ligue régionale : {e}")

            # Exécute les tâches asynchrones
            await asyncio.gather(*tasks)

        except Exception as e:
            self.logger.error(f"Erreur critique lors du scraping des poules régionales : {e}")
        finally:
            delete_output_directory(self.folder)
            self.logger.debug("Fin du scraping des poules régionales.")
            
            
    async def scrape_pools_from_league(self, league_code, league_name, league_page_url):
        scraped_pool_codes = set()
        try:
            if league_code not in ['LIMY', 'LIGY', 'LIGU', 'LIMART', 'LIRE']:
                self.logger.debug(f"Scraping des pools pour la ligue: {league_name} ({league_code})")
                league_page_url = league_page_url.replace('https://', 'http://')

                html_content = await self.fetch(league_page_url)
                if not html_content:
                    self.logger.error(f"Échec de la récupération du contenu HTML pour la ligue: {league_name}")
                    return

                soup = BeautifulSoup(html_content, 'html.parser')
                pool_links = soup.select('ul#menu > li > ul > li > ul > li > a[href*="poule="]')
                tasks = []

                for a_tag in pool_links:
                    try:
                        href = a_tag['href']
                        pool_code_match = re.search(r'poule=([^&]+)', href)
                        season_match = re.search(r'saison=([^&]+)', href)
                        if not pool_code_match or not season_match:
                            self.logger.warning(f"Informations manquantes dans l'URL: {href}")
                            continue
                        pool_code = pool_code_match.group(1)
                        raw_season = season_match.group(1)
                        pool_name = a_tag.get_text(strip=True)
                        raw_division_tag = a_tag.find_parent('ul').find_previous_sibling('a')
                        raw_division_name = raw_division_tag.get_text(strip=True) if raw_division_tag else ""
                        standardized = standardize_division_name(raw_division_name)

                        scraped_pool_codes.add(pool_code)

                        pool_data = {
                            "pool_code": pool_code,
                            "league_code": league_code,
                            "season": parse_season(raw_season),
                            "league_name": league_name,
                            "pool_name": pool_name,
                            "division_code": PoolDivisionCode.REG,
                            "division_name": standardized["division"],
                            "gender": standardized["gender"],
                            "raw_division_name": raw_division_name
                        }
                        pool = Pool(**pool_data)

                        new_pool = await add_or_update_pool(self.session, pool)
                        if new_pool:
                            task = handle_csv_download_and_parse(
                                self.session, new_pool.id, new_pool.league_code, new_pool.pool_code, raw_season, self.folder
                            )
                            tasks.append(task)

                    except Exception as e:
                        self.logger.error(f"Erreur lors du traitement d'une pool : {e}")

                await asyncio.gather(*tasks)

            await deactivate_pools(self.session, league_code, scraped_pool_codes)
            
        except Exception as e:
            self.logger.error(f"Erreur critique lors du scraping des pools pour la ligue {league_name} : {e}")

        self.logger.debug(f"Pools pour la ligue {league_name} ajoutées à la base de données.")