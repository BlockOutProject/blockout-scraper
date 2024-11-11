from datetime import datetime, timezone
import os
import shutil
import logging
import csv
from typing import Iterator

logger = logging.getLogger('blockout')

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
                'league_code': row['Entité'],
                'match_code': row['Match'],
                'club_a_id': row['EQA_no'],
                'club_b_id': row['EQB_no'],
                'team_a_name': row['EQA_nom'],
                'team_b_name': row['EQB_nom'],
                'match_date': row['Date'],
                'match_time': row['Heure'],
                'set': row['Set'].strip() or None,
                'score': row['Score'] or None,
                'venue': row['Salle'] or None,
                'referee1': row['Arb1'] or None,
                'referee2': row['Arb2'] or None,
            }
            
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


