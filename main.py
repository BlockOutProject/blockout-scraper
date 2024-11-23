import asyncio
import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timezone
from db import create_tables
from models.accumulating_handler import AccumulatingHandler
from scrapers.scraper_factory import ScraperFactory
from services.execution_logs_service import log_execution
from session_manager import get_db_session
from config.logger_config import logger

lock = asyncio.Lock()
accumulating_handler = AccumulatingHandler()
logger.addHandler(accumulating_handler)

async def main():
    """
    Fonction principale exécutant le scraping pour les pools nationales, régionales, et pro.
    """
    start_time = datetime.now(timezone.utc)
    with get_db_session() as db_session:
        async with lock:  
            try:
                logger.debug("Début du scraping...")
                create_tables()  # Crée les tables dans la base si elles n'existent pas

                async with aiohttp.ClientSession() as session:
                    scraper_types = ['pro', 'national', 'regional']
                    tasks = []

                    for scraper_type in scraper_types:
                        scraper = ScraperFactory.create_scraper(scraper_type, session)
                        tasks.append(scraper.scrape())

                    await asyncio.gather(*tasks)
                
                # Capturer l'heure de fin et calculer la durée de l'exécution
                end_time = datetime.now(timezone.utc)
                duration = int((end_time - start_time).total_seconds())  # Calculer la durée en secondes
                
                # Enregistrer un log de succès dans la base de données
                log_execution(db_session, start_time, duration, "Success", accumulating_handler.get_logs())
                
                logger.debug(f"Scraping terminé. Durée de l'exécution: {duration} secondes.")
            
            except Exception as e:
                logger.error(f"Erreur lors du scraping: {e}")
                # Enregistrer un log d'échec dans la base de données
                log_execution(db_session, start_time, 0, "Failed", accumulating_handler.get_logs())
            
            finally:
                accumulating_handler.clear_logs()
                #await log_started_matches()

def schedule_scraper():
    """
    Planifie l'exécution du scraping toutes les 10 minutes à l'aide d'APScheduler.
    """
    scheduler = AsyncIOScheduler()
    scheduler.add_job(main, 'interval', minutes=1, next_run_time=datetime.now(timezone.utc))
    scheduler.start()

if __name__ == "__main__":
    # Planifie le scraping avec APScheduler
    schedule_scraper()

    # Bloque le script pour éviter qu'il ne se termine
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass