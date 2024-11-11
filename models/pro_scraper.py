from models.scraper import Scraper


class ProScraper(Scraper):
    def __init__(self, session):
        super().__init__(session)
        self.folder = create_output_directory("Pro")
        self.raw_season = "2024/2025"  # À externaliser dans une configuration
        self.league_code = "AALNV"
        self.league_name = "PRO"
        self.pools_json = [
        {"code": "MSL", "pool_name": "Marmara SpikeLigue", "division_name": "Marmara SpikeLigue", "gender": "M", "lnv_url": "http://lnv-web.dataproject.com/CompetitionMatches.aspx?ID=115", "lnv_xml_url": "https://www.lnv.fr/xml/calendrier-LAM.xml"},
        {"code": "LBM", "pool_name": "Ligue B Masculine", "division_name": "Ligue B Masculine", "gender": "M", "lnv_url": "http://lnv-web.dataproject.com/CompetitionMatches.aspx?ID=116", "lnv_xml_url": "https://www.lnv.fr/xml/calendrier-LBM.xml"},
        {"code": "LAF", "pool_name": "Saforelle Power 6", "division_name": "Saforelle Power 6", "gender": "F", "lnv_url": "http://lnv-web.dataproject.com/CompetitionMatches.aspx?ID=113", "lnv_xml_url": "https://www.lnv.fr/xml/calendrier-LAF.xml"},
    ]

    async def scrape(self):
        tasks = []

        self.logger.debug("Début du scraping des poules professionnelles.")
        
        for pool_json in self.pools_json:
            pool_data = {
                "pool_code": pool_json['code'],
                "league_code": self.league_code,
                "season": parse_season(self.raw_season),
                "league_name": self.league_name,
                "pool_name": pool_json['pool_name'],
                "division_code": PoolDivisionCode.PRO.value,
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

        await asyncio.gather(*tasks)

        self.logger.debug("Poules professionnelles ajoutées à la base de données via API.")
        delete_output_directory(self.folder)

    async def execute_task_chain(self, pool_id, pool_code, season, gender, folder, lnv_url, lnv_xml_url):
        await handle_csv_download_and_parse(self.session, pool_id, self.league_code, pool_code, season, folder)
        await parse_and_update_matches(self.session, lnv_xml_url, pool_id)
        await add_match_live_code(self.session, lnv_url, pool_id, gender)