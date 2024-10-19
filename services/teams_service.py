from typing import Optional
from sqlalchemy.orm import Session
from errors_handler import handle_errors
import logging
from models.team import Team

logger = logging.getLogger('blockout')

@handle_errors
def add_or_update_team(
    session: Session,
    club_id: Optional[str],
    pool_id: int,
    team_name: str
) -> Team:
    """
    Ajoute ou met à jour une équipe dans la base de données. 
    Si l'équipe existe déjà, elle est mise à jour si nécessaire.

    Parameters:
    - session (Session): La session SQLAlchemy active.
    - club_id (Optional[str]): L'ID du club, si disponible.
    - pool_id (int): L'ID de la pool.
    - team_name (str): Le nom de l'équipe.

    Returns:
    - Team: L'objet Team ajouté ou mis à jour.
    """

    if not pool_id:
        raise ValueError("pool_id est obligatoire pour ajouter ou mettre à jour une équipe.")
    if not team_name:
        raise ValueError("team_name est obligatoire pour ajouter ou mettre à jour une équipe.")

    team = get_team(session, pool_id, team_name)

    if team:
        if not team.active:
            team.active = True
            logger.info(f"Équipe réactivée : {team_name} (Pool ID: {pool_id})")
    else:
        team = Team(
            club_id=club_id,
            pool_id=pool_id,
            team_name=team_name,
            active=True  
        )
        session.add(team)
        session.flush() 
        logger.info(f"Nouvelle équipe ajoutée: {team_name} (Club ID: {club_id})")
    
    return team

@handle_errors
def get_team(session: Session, pool_id: int, team_name: str) -> Optional[Team]:
    """
    Récupère une équipe depuis la base de données pour une paire donnée de pool_id et club_id.

    Parameters:
    - session (Session): La session SQLAlchemy active.
    - pool_id (int): L'ID de la pool.
    - team_name (str): Le nom de l'équipe.

    Returns:
    - Optional[Team]: L'équipe si elle existe, sinon None.
    """
    team = session.query(Team).filter_by(
        pool_id=pool_id,
        team_name=team_name
    ).first()
    if team:
        logger.debug(f"Équipe trouvée: {team.team_name} (Pool ID: {pool_id})")
    else:
        logger.debug(f"Aucune équipe trouvée pour Team Name: {team_name} et Pool ID: {pool_id}")
    return team

@handle_errors
def desactivate_teams(session, pool_id, scraped_team_names):
    """
    Désactive les équipes qui existent en base de données mais n'ont pas été scrapées pour une pool spécifique.

    Parameters:
    - session: La session SQLAlchemy active.
    - pool_id: L'ID de la pool dont on veut désactiver les équipes.
    - scraped_team_names (set): Un ensemble des noms d'équipes qui ont été scrapés pour cette pool.
    """

    # Récupérer toutes les équipes actives de la pool qui ne sont pas dans les équipes scrapées
    teams_to_deactivate = session.query(Team).filter(
        Team.active == True,
        Team.pool_id == pool_id,
        Team.team_name.notin_(scraped_team_names)
    ).all()

    # Désactiver ces équipes
    for team in teams_to_deactivate:
        team.active = False
        session.add(team)
        logger.info(f"L'équipe {team.team_name} dans la poule {team.pool.pool_code} a été désactivée.")
        