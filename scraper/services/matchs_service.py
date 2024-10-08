# matchs_service.py
from typing import Optional
from sqlalchemy.orm import Session
from db import Match
from datetime import datetime
from errors_handler import handle_errors
import logging

# Importer le logger
logger = logging.getLogger('myvolley')

@handle_errors
def add_match(
    session: Session,
    league_code: str,
    match_code: str,
    pool_id: int,
    team_a_id: int,
    team_b_id: int,
    match_date: datetime,
    score: Optional[str],
    status: str,
    venue: Optional[str] = None,
    referee1: Optional[str] = None,
    referee2: Optional[str] = None
) -> Match:
    """
    Ajoute un match à la base de données ou le met à jour s'il existe déjà.

    Parameters:
    - session (Session): La session SQLAlchemy active.
    - league_code (str): Le code de la ligue.
    - match_code (str): Le code du match.
    - pool_id (int): L'ID de la pool.
    - team_a_id (int): L'ID de l'équipe A.
    - team_b_id (int): L'ID de l'équipe B.
    - match_date (datetime): La date et l'heure du match.
    - score (Optional[str]): Le score final, si disponible.
    - status (str): Le statut du match ('completed', 'upcoming', etc.).
    - venue (Optional[str]): Le lieu du match, si disponible.
    - referee1 (Optional[str]): Le nom du premier arbitre, si disponible.
    - referee2 (Optional[str]): Le nom du second arbitre, si disponible.

    Returns:
    - Match: L'objet Match ajouté ou mis à jour.
    """
    existing_match = session.query(Match).filter_by(
        league_code=league_code,
        match_code=match_code
    ).first()

    if existing_match:
        # Mise à jour du match existant
        existing_match.team_a_id = team_a_id
        existing_match.team_b_id = team_b_id
        existing_match.match_date = match_date
        existing_match.score = score
        existing_match.status = status
        existing_match.venue = venue
        existing_match.referee1 = referee1
        existing_match.referee2 = referee2
        logger.debug(f"Match mis à jour: {match_code} ({league_code})")
        return existing_match
    else:
        # Ajout d'un nouveau match
        new_match = Match(
            league_code=league_code,
            match_code=match_code,
            pool_id=pool_id,
            team_a_id=team_a_id,
            team_b_id=team_b_id,
            match_date=match_date,
            score=score,
            status=status,
            venue=venue,
            referee1=referee1,
            referee2=referee2
        )
        session.add(new_match)
        session.flush()
        logger.debug(f"Nouveau match ajouté: {match_code} ({league_code})")
        return new_match

@handle_errors
def clear_matchs_table(session: Session) -> None:
    """
    Vide la table 'matches' dans la base de données.

    Parameters:
    - session (Session): La session SQLAlchemy active.
    """
    deleted = session.query(Match).delete()
    session.commit()
    logger.info(f"Table 'matches' vidée. {deleted} enregistrements supprimés.")