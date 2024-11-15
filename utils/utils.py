import json
import re
import logging
from typing import Optional

logger = logging.getLogger('blockout')

try:
    with open('config/mapping/standardized_divisions.json', 'r', encoding='utf-8') as f:
        standardized_divisions = json.load(f)
except Exception as e:
    logger.error(f"Erreur lors du chargement de 'standardized_divisions.json': {e}")
    standardized_divisions = {}

def standardize_division_name(division_name: str) -> dict:
    """
    Standardise le nom d'une division en fonction des variations prédéfinies.
    """
    try:
        for category, genders in standardized_divisions.items():
            for gender, variations in genders.items():
                if division_name in variations:
                    logger.debug(f"Division standardisée trouvée: {division_name} -> {category}, Genre: {gender}")
                    return {"division": category, "gender": gender}
        logger.debug(f"Division non standardisée: {division_name}")
        return {"division": division_name.strip(), "gender": None}
    except Exception as e:
        logger.error(f"[standardize_division_name] Erreur lors de la standardisation de '{division_name}': {e}")
        raise 
    
def parse_season(season_str: str) -> int:
    """
    Convertit une chaîne de saison 'YYYY/YYYY' en un entier combiné 'YYYYYY' 
    en prenant les deux derniers chiffres de chaque année.
    """
    try:
        # Séparer les années et prendre les deux derniers chiffres de chaque année
        start_year, end_year = season_str.split('/')
        start_year_last_two = start_year[-2:]  # Derniers chiffres de l'année de début
        end_year_last_two = end_year[-2:]  # Derniers chiffres de l'année de fin

        # Concaténer les deux derniers chiffres des deux années et convertir en entier
        combined_years = int(start_year_last_two + end_year_last_two)
        
        logger.debug(f"Saison parsée: {season_str} -> {combined_years}")
        return combined_years
    except Exception as e:
        logger.error(f"[parse_season] Erreur inattendue lors du parsing de la saison '{season_str}': {e}")
        raise 
    
def extract_season_from_url(url: str) -> Optional[str]:
    """
    Extrait la saison à partir de l'URL.
    """
    try:
        match = re.search(r'/(\d{4})-(\d{4})/', url)
        if match:
            start_year, end_year = match.groups()
            season = f"{start_year}/{end_year}"
            logger.debug(f"Saison extraite de l'URL '{url}': {season}")
            return season
        logger.warning(f"Aucune saison trouvée dans l'URL: {url}")
        return None
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction de la saison depuis l'URL '{url}': {e}")
        raise 

def extract_national_division(pool_name: str) -> str:
    """
    Extrait la division nationale du nom de la poule.
    """
    try:
        division_name = pool_name.split('Poule')[0].strip()
        logger.debug(f"Division nationale extraite du nom de poule '{pool_name}': {division_name}")
        return division_name
    except Exception as e:
        logger.error(f"[extract_national_division] Erreur inattendue lors de l'extraction de la division pour '{pool_name}': {e}")
        raise 

