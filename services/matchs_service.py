from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from errors_handler import handle_errors
import logging
from models.match import Match, MatchStatus

logger = logging.getLogger('blockout')

@handle_errors
def add_or_update_match(
    session: Session,
    league_code: str,
    match_code: str,
    pool_id: int,
    team_a_id: int,
    team_b_id: int,
    match_date: datetime,
    set: Optional[str],
    score: Optional[str],
    venue: Optional[str] = None,
    referee1: Optional[str] = None,
    referee2: Optional[str] = None
) -> Match:
    """
    Ajoute ou met à jour un match dans la base de données.
    Si le match existe déjà, il est mis à jour. Sinon, il est ajouté.
    Logue les modifications détectées.
    """

    if not match_code:
        raise ValueError("match_code est obligatoire pour ajouter un match.")
    if not league_code:
        raise ValueError("league_code est obligatoire pour ajouter un match.")
    if not pool_id:
        raise ValueError("pool_id est obligatoire pour ajouter un match.")
    if not team_a_id:
        raise ValueError("team_a_id est obligatoire pour ajouter un match.")
    if not team_b_id:
        raise ValueError("team_b_id est obligatoire pour ajouter un match.")
    if not match_date:
        raise ValueError("match_date est obligatoire pour ajouter un match.")

    existing_match = session.query(Match).filter_by(
        league_code=league_code,
        match_code=match_code
    ).first()
    
    status = MatchStatus.COMPLETED if set and score else MatchStatus.UPCOMING

    if not existing_match:
        new_match = Match(
            league_code=league_code,
            match_code=match_code,
            pool_id=pool_id,
            team_a_id=team_a_id,
            team_b_id=team_b_id,
            match_date=match_date,
            set=set,
            score=score,
            status=status,
            venue=venue,
            referee1=referee1,
            referee2=referee2
        )
        session.add(new_match)
        session.flush()
        logger.info(f"Nouveau match ajouté: {match_code} ({league_code})")
        return new_match
    else:
        changes = []

        if existing_match.team_a_id != team_a_id:
            changes.append(f"team_a_id: {existing_match.team_a_id} -> {team_a_id}")
            existing_match.team_a_id = team_a_id
        
        if existing_match.team_b_id != team_b_id:
            changes.append(f"team_b_id: {existing_match.team_b_id} -> {team_b_id}")
            existing_match.team_b_id = team_b_id
        
        if existing_match.match_date != match_date:
            changes.append(f"match_date: {existing_match.match_date} -> {match_date}")
            existing_match.match_date = match_date
        
        if existing_match.set != set:
            changes.append(f"set: {existing_match.set} -> {set}")
            existing_match.set = set
        
        if existing_match.score != score:
            changes.append(f"score: {existing_match.score} -> {score}")
            existing_match.score = score
        
        if existing_match.status != status:
            changes.append(f"status: {existing_match.status.value} -> {status.value}")
            existing_match.status = status
        
        if existing_match.venue != venue:
            changes.append(f"venue: {existing_match.venue} -> {venue}")
            existing_match.venue = venue
        
        if existing_match.referee1 != referee1:
            changes.append(f"referee1: {existing_match.referee1} -> {referee1}")
            existing_match.referee1 = referee1
        
        if existing_match.referee2 != referee2:
            changes.append(f"referee2: {existing_match.referee2} -> {referee2}")
            existing_match.referee2 = referee2

        if changes:
            logger.info(f"Match {match_code} ({league_code}) mis à jour. Changements: {', '.join(changes)}")

        return existing_match
    
@handle_errors  
def desactivate_matches(session, pool_id, scraped_match_codes):
    """
    Désactive les matchs qui existent en base de données mais n'ont pas été scrapés pour une pool spécifique.

    Parameters:
    - session: La session SQLAlchemy active.
    - pool_id: L'ID de la pool dont on veut désactiver les matchs.
    - scraped_match_codes (set): Un ensemble des codes de matchs qui ont été scrapés pour cette pool.
    """

    # Récupérer tous les matchs actifs de la pool qui ne sont pas dans les matchs scrapés
    matches_to_desactivate = session.query(Match).filter(
        Match.active == True,
        Match.pool_id == pool_id,
        Match.match_code.notin_(scraped_match_codes)
    ).all()

    # Désactiver ces matchs
    for match in matches_to_desactivate:
        match.active = False
        session.add(match)
        logger.info(f"Le match {match.match_code} dans la poule {match.pool.pool_code} a été désactivé.")
        
def log_started_matches(session: Session):
    """
    Logue les matchs qui ont commmencé.
    
    Parameters:
    - session: La session SQLAlchemy active.
    """
    current_time = datetime.now(timezone.utc)

    started_matches = session.query(Match).filter(
        Match.active == True,
        Match.status == MatchStatus.UPCOMING,
        Match.match_date <= current_time  # On récupère uniquement les matchs avec une date inférieure ou égale à l'heure actuelle
    ).all()

    if started_matches:
        print(f"Matchs en cours :")
        for match in started_matches:
            print(f"Match {match.match_code} dans la ligue {match.league_code}: "
                        f"équipe A ({match.team_a_id}) vs équipe B ({match.team_b_id}) "
                        f"à {match.match_date.strftime('%Y-%m-%d %H:%M:%S')} à {match.venue}")
