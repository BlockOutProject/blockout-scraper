import os
import json
import re
import csv
from datetime import datetime, timezone
import logging
import shutil
from typing import Iterator, Optional
from downloader import download_csv
from errors_handler import handle_errors
from services.teams_service import add_or_update_team, desactivate_teams
from session_manager import get_db_session
from services.matchs_service import add_or_update_match, desactivate_matches

logger = logging.getLogger('blockout')

def create_output_directory(league: str) -> str:
    """
    Crée un répertoire de sortie sous la structure CSV/league, 
    nommé avec la date et l'heure actuelles.

    Parameters:
    - league (str): Le nom de la ligue.

    Returns:
    - str: Le chemin du répertoire créé.
    """
    now = datetime.now(timezone.utc)
    folder_name = now.strftime(f"CSV/{league}/%Y%m%d_%H%M%S")
    os.makedirs(folder_name, exist_ok=True)
    logger.debug(f"Répertoire de sortie créé: {folder_name}")
    return folder_name

try:
    with open('standardized_divisions.json', 'r', encoding='utf-8') as f:
        standardized_divisions = json.load(f)
except Exception as e:
    logger.error(f"Erreur lors du chargement de 'standardized_divisions.json': {e}")
    standardized_divisions = {}

def standardize_division_name(division_name: str) -> dict:
    """
    Standardise le nom d'une division en fonction des variations prédéfinies.

    Parameters:
    - division_name (str): Le nom de la division à standardiser.

    Returns:
    - dict: Un dictionnaire contenant le nom standardisé et le genre.
    """
    for category, genders in standardized_divisions.items():
        for gender, variations in genders.items():
            if division_name in variations:
                logger.debug(f"Division standardisée trouvée: {division_name} -> {category}, Genre: {gender}")
                return {"division": category, "gender": gender}
    # Retourne la division originale si aucune correspondance n'est trouvée
    logger.debug(f"Division non standardisée: {division_name}")
    return {"division": division_name.strip(), "gender": None}

def parse_season(season_str: str) -> int:
    """
    Convertit une chaîne de saison 'YYYY/YYYY' en un entier 'YYYY'.

    Parameters:
    - season_str (str): La chaîne de la saison au format 'YYYY/YYYY'.

    Returns:
    - int: L'année de début de la saison.

    Raises:
    - ValueError: Si le format de la saison est invalide.
    """
    try:
        start_year = int(season_str.split('/')[0])
        logger.debug(f"Saison parsée: {season_str} -> {start_year}")
        return start_year
    except Exception as e:
        logger.error(f"Erreur lors du parsing de la saison '{season_str}': {e}")
        raise ValueError(f"Erreur lors du traitement de la saison: {e}")

def extract_season_from_url(url: str) -> Optional[str]:
    """
    Extrait la saison à partir de l'URL.

    Parameters:
    - url (str): L'URL à analyser.

    Returns:
    - Optional[str]: La saison au format 'YYYY/YYYY' ou None si non trouvée.
    """
    match = re.search(r'/(\d{4})-(\d{4})/', url)
    if match:
        start_year, end_year = match.groups()
        season = f"{start_year}/{end_year}"
        logger.debug(f"Saison extraite de l'URL '{url}': {season}")
        return season
    logger.warning(f"Aucune saison trouvée dans l'URL: {url}")
    return None

def extract_national_division(pool_name: str) -> str:
    """
    Extrait la division nationale du nom de la poule.

    Parameters:
    - pool_name (str): Le nom de la poule.

    Returns:
    - str: La division nationale extraite.
    """
    division_name = pool_name.split('Poule')[0].strip()
    logger.debug(f"Division nationale extraite du nom de poule '{pool_name}': {division_name}")
    return division_name

def parse_csv(file_path: str) -> Iterator[dict]:
    """
    Parse un fichier CSV et génère chaque ligne sous forme de dictionnaire.

    Parameters:
    - file_path (str): Le chemin du fichier CSV.

    Yields:
    - dict: Un dictionnaire représentant une ligne du CSV.
    """
    logger.debug(f"Parsing du fichier CSV: {file_path}")
    with open(file_path, encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            yield {
                'league_code': row.get('Entité'),
                'match_code': row.get('Match'),
                'club_a_id': row.get('EQA_no'),
                'club_b_id': row.get('EQB_no'),
                'team_a_name': row.get('EQA_nom'),
                'team_b_name': row.get('EQB_nom'),
                'match_date': row.get('Date'),
                'match_time': row.get('Heure'),
                'set': row.get('Set'),
                'score': row.get('Score'),
                'venue': row.get('Salle'),
                'referee1': row.get('Arb1'),
                'referee2': row.get('Arb2'),
            }

def parse_date(date_str: str, time_str: str) -> Optional[datetime]:
    """
    Convertit des chaînes de date et d'heure en objet datetime.

    Parameters:
    - date_str (str): La date au format 'YYYY-MM-DD'.
    - time_str (str): L'heure au format 'HH:MM'.

    Returns:
    - Optional[datetime]: L'objet datetime correspondant ou None en cas d'erreur.
    """
    try:
        date_time = datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M')
        logger.debug(f"Date parsée: {date_str} {time_str} -> {date_time}")
        return date_time
    except ValueError as e:
        logger.warning(f"Erreur lors du parsing de la date '{date_str} {time_str}': {e}")
        return None

@handle_errors
async def fetch(http_session, url: str) -> Optional[str]:
    """
    Récupère le contenu d'une URL de manière asynchrone.

    Parameters:
    - http_session: La session aiohttp.
    - url (str): L'URL à récupérer.

    Returns:
    - Optional[str]: Le contenu de la réponse, ou None en cas d'erreur.
    """
    try:
        async with http_session.get(url) as response:
            response.raise_for_status()
            content = await response.content.read()
            logger.debug(f"Contenu récupéré depuis l'URL: {url}")
            return content
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'URL '{url}': {e}")
        return None

@handle_errors
async def handle_csv_download_and_parse(
    http_session,
    pool_id: int,
    league_code: str,
    pool_code: str,
    season: str,
    folder: str
) -> None:
    """
    Gère le téléchargement et le parsing du CSV de manière asynchrone.

    Parameters:
    - http_session: La session aiohttp.
    - pool_id (int): L'ID de la pool.
    - league_code (str): Le code de la ligue.
    - pool_code (str): Le code de la pool.
    - season (str): La saison.
    - folder (str): Le dossier de sauvegarde.
    """
    logger.debug(f"Téléchargement du CSV pour Pool ID: {pool_id}, League Code: {league_code}, Pool Code: {pool_code}")
    csv_path = await download_csv(http_session, league_code, pool_code, season, folder)
    if csv_path:
        logger.debug(f"CSV téléchargé avec succès: {csv_path}")
        await parse_and_add_matches_from_csv(pool_id, csv_path)
    else:
        logger.error(f"Échec du téléchargement du CSV pour Pool Code: {pool_code}")

@handle_errors
async def parse_and_add_matches_from_csv(pool_id: int, csv_path: str) -> None:
    """
    Parse le fichier CSV et ajoute les matchs à la base de données.

    Parameters:
    - pool_id (int): L'ID de la pool.
    - csv_path (str): Le chemin du fichier CSV.
    """
    logger.debug(f"Parsing et ajout des matchs depuis le CSV: {csv_path}")
    scraped_team_names = set()
    scraped_match_codes = set()
    with get_db_session() as session:
        for data in parse_csv(csv_path):
            club_a_id = data['club_a_id']
            club_b_id = data['club_b_id']
            if club_a_id and club_b_id:
                match_datetime = parse_date(data['match_date'], data['match_time'])
                if not match_datetime:
                    logger.warning(f"Date invalide pour le match {data['match_code']}. Match ignoré.")
                    continue 

                team_a = add_or_update_team(
                    session,
                    pool_id=pool_id,
                    club_id=data['club_a_id'],
                    team_name=data['team_a_name']
                )

                team_b = add_or_update_team(
                    session,
                    pool_id=pool_id,
                    club_id=data['club_b_id'],
                    team_name=data['team_b_name']
                )
                
                scraped_team_names.add(team_a.team_name)
                scraped_team_names.add(team_b.team_name)

                match = add_or_update_match(
                    session,
                    league_code=data['league_code'],
                    match_code=data['match_code'],
                    pool_id=pool_id,
                    team_a_id=team_a.id,
                    team_b_id=team_b.id,
                    match_date=match_datetime,
                    set=data['set'],
                    score=data['score'],
                    venue=data['venue'],
                    referee1=data['referee1'],
                    referee2=data['referee2']
                )
                
                scraped_match_codes.add(match.match_code)
                
        desactivate_teams(session, pool_id, scraped_team_names)
        desactivate_matches(session, pool_id, scraped_match_codes)
        logger.debug(f"Matchs ajoutés depuis le CSV: {csv_path}")

def delete_output_directory(folder_path: str) -> None:
    """
    Supprime un répertoire de sortie et tout son contenu.

    Parameters:
    - folder_path (str): Le chemin du répertoire à supprimer.
    """
    try:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            logger.debug(f"Répertoire supprimé: {folder_path}")
        else:
            logger.warning(f"Tentative de suppression : le répertoire {folder_path} n'existe pas.")
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du répertoire : {str(e)}")
        raise