import html
from typing import Optional
import aiohttp
from abc import ABC, abstractmethod
import chardet
from config.logger_config import logger

class Scraper(ABC):
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session        

    async def fetch(self, url: str) -> str:
        """
        Récupère le contenu d'une URL en gérant les problèmes d'encodage.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0"
            }
            async with self.session.get(url, headers=headers, ssl=False) as response:
                response.raise_for_status()

                raw_content = await response.content.read()
                detected_encoding = chardet.detect(raw_content)['encoding']
                encoding = detected_encoding or 'utf-8'
                decoded_content = raw_content.decode(encoding, errors='replace')
                decoded_content = html.unescape(decoded_content)

                return decoded_content
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'URL '{url}' : {e}")
            raise

    @abstractmethod
    async def scrape(self):
        """Méthode principale de scraping à implémenter par les sous-classes."""
        pass