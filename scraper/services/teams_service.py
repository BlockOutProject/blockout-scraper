# teams_service.py
from typing import Optional
from sqlalchemy.orm import Session
from db import Team
from errors_handler import handle_errors
import logging

# Importer le logger
logger = logging.getLogger('myvolley')

@handle_errors
def add_team(
    session: Session,
    club_id: Optional[str],
    pool_id: int,
    team_name: str
) -> Team:
    """
    Ajoute une équipe à la base de données ou la récupère si elle existe déjà.

    Parameters:
    - session (Session): La session SQLAlchemy active.
    - club_id (Optional[str]): L'ID du club, si disponible.
    - pool_id (int): L'ID de la pool.
    - team_name (str): Le nom de l'équipe.

    Returns:
    - Team: L'objet Team ajouté ou existant.
    """
    existing_team = session.query(Team).filter_by(
        club_id=club_id,
        pool_id=pool_id
    ).first()

    if not existing_team:
        new_team = Team(
            club_id=club_id,
            pool_id=pool_id,
            team_name=team_name
        )
        session.add(new_team)
        session.flush()
        logger.debug(f"Nouvelle équipe ajoutée: {team_name} (Club ID: {club_id})")
        return new_team
    else:
        logger.debug(f"Équipe existante récupérée: {team_name} (Club ID: {club_id})")
        return existing_team

@handle_errors
def add_team_bulk(session: Session, teams: list) -> None:
    """
    Ajoute plusieurs équipes à la base de données en une seule transaction.

    Parameters:
    - session (Session): La session SQLAlchemy active.
    - teams (list of dict): Liste des équipes avec 'club_id', 'pool_id', 'team_name'.
    """
    for team_data in teams:
        add_team(
            session,
            club_id=team_data['club_id'],
            pool_id=team_data['pool_id'],
            team_name=team_data['team_name']
        )
    logger.info(f"{len(teams)} équipes traitées en batch.")

@handle_errors
def clear_teams_table(session: Session) -> None:
    """
    Vide la table 'teams' dans la base de données.

    Parameters:
    - session (Session): La session SQLAlchemy active.
    """
    deleted = session.query(Team).delete()
    session.commit()
    logger.info(f"Table 'teams' vidée. {deleted} enregistrements supprimés.")

@handle_errors
def get_team(session: Session, pool_id: int, club_id: Optional[str]) -> Optional[Team]:
    """
    Récupère une équipe depuis la base de données pour une paire donnée de pool_id et club_id.

    Parameters:
    - session (Session): La session SQLAlchemy active.
    - pool_id (int): L'ID de la pool.
    - club_id (Optional[str]): L'ID du club.

    Returns:
    - Optional[Team]: L'équipe si elle existe, sinon None.
    """
    team = session.query(Team).filter_by(
        pool_id=pool_id,
        club_id=club_id
    ).first()
    if team:
        logger.debug(f"Équipe trouvée: {team.team_name} (Club ID: {club_id})")
    else:
        logger.debug(f"Aucune équipe trouvée pour Club ID: {club_id} et Pool ID: {pool_id}")
    return team

@handle_errors
def get_or_create_team(
    session: Session,
    pool_id: int,
    club_id: Optional[str],
    team_name: str
) -> int:
    """
    Récupère l'équipe à partir de la paire (pool_id, club_id) ou crée l'équipe si elle n'existe pas.

    Parameters:
    - session (Session): La session SQLAlchemy active.
    - pool_id (int): L'ID de la pool.
    - club_id (Optional[str]): L'ID du club.
    - team_name (str): Le nom de l'équipe.

    Returns:
    - int: L'ID de l'équipe (existante ou nouvellement créée).
    """
    team = get_team(session, pool_id, club_id)
    if team:
        return team.id
    else:
        new_team = add_team(session, club_id, pool_id, team_name)
        return new_team.id