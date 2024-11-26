import aiohttp
import asyncio
from config.logger_config import logger

MAX_RETRIES = 3       # Nombre maximum de tentatives de téléchargement
RETRY_DELAY = 2       # Délai en secondes entre chaque tentative en cas d'échec
TIMEOUT = aiohttp.ClientTimeout(total=30)  # Timeout de 30 secondes pour chaque requête
SEM = asyncio.Semaphore(10)  # Limiter à 20 téléchargements simultanés

async def download_csv(
    session: aiohttp.ClientSession,
    league_code: str,
    pool_code: str,
    raw_season: str,
    folder: str
) -> str:
    """
    Télécharge un fichier CSV contenant les données spécifiques d'une pool.

    Parameters:
    - session (aiohttp.ClientSession): La session aiohttp active.
    - league_code (str): Le code de la ligue.
    - pool_code (str): Le code de la pool.
    - season (str): La saison.
    - folder (str): Le dossier où le fichier CSV sera sauvegardé.

    Returns:
    - str: Le chemin du fichier CSV téléchargé, ou None en cas d'échec.
    """
    download_url = "http://www.ffvbbeach.org/ffvbapp/resu/vbspo_calendrier_export.php"
    data = {
        'cal_saison': raw_season,
        'cal_codent': league_code,
        'cal_codpoule': pool_code,
    }
    filename = f"{folder}/poule_{league_code}_{pool_code}.csv"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Limiter les téléchargements simultanés avec le sémaphore
            async with SEM:
                async with session.post(download_url, data=data, timeout=TIMEOUT) as response:
                    if response.status == 200:
                        content = await response.read()
                        # Tenter de décoder le contenu
                        try:
                            content = content.decode('utf-8')
                        except UnicodeDecodeError:
                            content = content.decode('ISO-8859-1')
                        # Écrire le contenu dans le fichier
                        with open(filename, 'w', encoding='utf-8', errors='replace') as f:
                            f.write(content)
                        logger.debug(f"CSV téléchargé avec succès: {filename}")
                        return filename  # Retourner le chemin du fichier après téléchargement réussi
                    else:
                        logger.warning(f"Tentative {attempt}/{MAX_RETRIES}: Échec du téléchargement pour {league_code}_{pool_code}, statut HTTP: {response.status}")
        except asyncio.TimeoutError:
            logger.error(f"Tentative {attempt}/{MAX_RETRIES}: Timeout lors du téléchargement pour {league_code}_{pool_code}")
        except aiohttp.ClientError as e:
            logger.error(f"Tentative {attempt}/{MAX_RETRIES}: Erreur réseau pour {league_code}_{pool_code} - {e}")
        except Exception as e:
            logger.error(f"Tentative {attempt}/{MAX_RETRIES}: Erreur inattendue pour {league_code}_{pool_code} - {e}")

        if attempt < MAX_RETRIES:
            logger.debug(f"Attente de {RETRY_DELAY} secondes avant la prochaine tentative...")
            await asyncio.sleep(RETRY_DELAY)  # Attendre avant de réessayer
        else:
            logger.error(f"Échec du téléchargement pour {league_code}_{pool_code} après {MAX_RETRIES} tentatives.")

    return None