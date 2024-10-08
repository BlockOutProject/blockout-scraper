import asyncio
import aiohttp
from pro_scraper import scrape_pro_pools
from national_scraper import scrape_national_pools
from regional_scraper import scrape_regional_pools

async def main():
    
    async with aiohttp.ClientSession() as http_session:
        # Lancer le scraping national et régional simultanément
        await asyncio.gather(
            scrape_national_pools(http_session),
            scrape_regional_pools(http_session),
            scrape_pro_pools(http_session)
        )

if __name__ == "__main__":
    asyncio.run(main())