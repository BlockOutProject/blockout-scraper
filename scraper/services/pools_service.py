# pools_service.py
from typing import Optional
from sqlalchemy.orm import Session
from db import Pool
from errors_handler import handle_errors
import logging

# Importer le logger
logger = logging.getLogger('myvolley')

@handle_errors
def add_pool(
    session: Session,
    pool_code: str,
    league_code: str,
    season: int,
    league_name: str,
    pool_name: str,
    division: str,
    gender: Optional[str],
    raw_division: Optional[str] = None
) -> Pool:
    """
    Ajoute une pool à la base de données ou la récupère si elle existe déjà.

    Parameters:
    - session (Session): La session SQLAlchemy active.
    - pool_code (str): Le code de la pool.
    - league_code (str): Le code de la ligue.
    - season (int): L'année de la saison.
    - league_name (str): Le nom de la ligue.
    - pool_name (str): Le nom de la pool.
    - division (str): La division de la pool.
    - gender (Optional[str]): Le genre ('M', 'F', ou None).
    - raw_division (Optional[str]): Le nom brut de la division, si disponible.

    Returns:
    - Pool: L'objet Pool ajouté ou existant.
    """
    existing_pool = session.query(Pool).filter_by(
        pool_code=pool_code,
        league_code=league_code,
        season=season
    ).first()

    if not existing_pool:
        new_pool = Pool(
            pool_code=pool_code,
            league_code=league_code,
            season=season,
            league_name=league_name,
            pool_name=pool_name,
            division=division,
            gender=gender,
            raw_division=raw_division
        )
        session.add(new_pool)
        session.flush()
        logger.debug(f"Nouvelle pool ajoutée: {pool_name} ({pool_code})")
        return new_pool
    else:
        logger.debug(f"Pool existante récupérée: {pool_name} ({pool_code})")
        return existing_pool

@handle_errors
def clear_pool_table(session: Session) -> None:
    """
    Vide la table 'pools' dans la base de données.

    Parameters:
    - session (Session): La session SQLAlchemy active.
    """
    deleted = session.query(Pool).delete()
    session.commit()
    logger.info(f"Table 'pools' vidée. {deleted} enregistrements supprimés.")