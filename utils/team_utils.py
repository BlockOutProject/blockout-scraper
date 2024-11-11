import json
from typing import Optional
import unicodedata
import logging

from utils.exceptions import AliasNotFoundError, TeamAliasError

logger = logging.getLogger('blockout')

# Chargement du fichier JSON contenant les alias
try:
    with open('config/mapping/team_aliases.json', 'r', encoding='utf-8') as f:
        team_aliases = json.load(f)
except Exception as e:
    logger.error(f"Erreur lors du chargement de 'team_aliases': {e}")
    team_aliases = {}

def is_name_in_aliases(name: str) -> bool:
    """
    Vérifie si un nom d'équipe est présent dans les alias définis pour les équipes.
    """
    try:
        for team in team_aliases.get('teams', []):  # Utilise `.get` pour éviter KeyError
            all_aliases = [team['full']] + team.get('aliases', [])  # Gère l'absence de 'aliases'
            if name in all_aliases:
                logger.debug(f"Nom trouvé dans les alias: {name}")
                return True
        logger.debug(f"Nom non trouvé dans les alias: {name}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue dans is_name_in_aliases : {str(e)}")
        raise TeamAliasError(f"Erreur inattendue lors de la vérification des alias pour '{name}'") from e

def remove_accents(text: str) -> str:
    """
    Supprime les accents d'un texte.
    """
    return ''.join(
        c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'
    )

def get_full_team_name(name: str, gender: str) -> Optional[str]:
    """
    Récupère le nom complet de l'équipe correspondant au nom donné en tenant compte du genre.
    """
    try:
        name_normalized = remove_accents(name).upper()
        logger.debug(f"Recherche du nom complet pour '{name_normalized}' avec genre '{gender}'")
        
        for team in team_aliases.get('teams', []):
            if team.get('gender') == gender:
                aliases_normalized = [remove_accents(alias).upper() for alias in team.get('aliases', [])]
                if name_normalized in aliases_normalized:
                    logger.debug(f"Nom complet trouvé : {team['full']} pour {name_normalized}")
                    return team['full']
        
        logger.warning(f"Aucun alias trouvé pour '{name}' avec le genre '{gender}'")
        raise AliasNotFoundError(f"Nom ou alias non trouvé : {name}, Genre attendu : {gender}")
    except AliasNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue dans get_full_team_name : {e}")
        raise TeamAliasError(f"Erreur inattendue lors de la recherche du nom complet pour '{name}'") from e