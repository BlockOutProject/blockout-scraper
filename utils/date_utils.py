import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger('blockout')

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
