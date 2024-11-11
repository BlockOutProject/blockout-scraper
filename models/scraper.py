import aiohttp
import logging
from abc import ABC, abstractmethod

class Scraper(ABC):
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.logger = logging.getLogger(self.__class__.__name__)

    async def fetch(self, url: str) -> str:
        """Récupère le contenu d'une URL."""
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                content = await response.text()
                return content
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération de l'URL '{url}': {e}")
            raise

    @abstractmethod
    async def scrape(self):
        """Méthode principale de scraping à implémenter par les sous-classes."""
        pass