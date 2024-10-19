from typing import Optional
from sqlalchemy.orm import Session
from errors_handler import handle_errors
import logging
from models.match import Match
from models.pool import Pool
from models.team import Team

logger = logging.getLogger('blockout')

@handle_errors
def add_or_update_pool(
    session: Session,
    pool_code: str,
    league_code: str,
    season: int,
    league_name: str,
    pool_name: str,
    division_code: str,
    division_name: str,
    gender: Optional[str],
    raw_division_name: Optional[str] = None
) -> Pool:
    """
    Crée une pool ou met à jour une pool existante dans la base de données.
    Si une pool est mise à jour, un log détaillé des changements est enregistré.

    Parameters:
    - session (Session): La session SQLAlchemy active.
    - pool_code (str): Le code de la pool.
    - league_code (str): Le code de la ligue.
    - season (int): L'année de la saison.
    - league_name (str): Le nom de la ligue.
    - pool_name (str): Le nom de la pool.
    - division_code (str): Le code de la division de la pool.
    - division_name (str): La division de la pool.
    - gender (Optional[str]): Le genre ('M', 'F', ou None).
    - raw_division_name (Optional[str]): Le nom brut de la division, si disponible.

    Returns:
    - Pool: L'objet Pool créé ou mis à jour.
    """
    
    if not pool_code:
        raise ValueError("pool_code est obligatoire pour ajouter une pool.")
    if not league_code:
        raise ValueError("league_code est obligatoire pour ajouter une pool.")
    if not season:
        raise ValueError("season est obligatoire pour ajouter une pool.")
    if not pool_name:
        raise ValueError("pool_name est obligatoire pour ajouter une pool.")
    if not division_code:
        raise ValueError("division_code est obligatoire pour ajouter une pool.")
    if not division_name:
        raise ValueError("division_name est obligatoire pour ajouter une pool.")
    

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
            division_code=division_code,
            division_name=division_name,
            gender=gender,
            raw_division_name=raw_division_name,
            active=True  # Nouvelle pool est active par défaut
        )
        session.add(new_pool)
        session.flush()  # Flush pour obtenir l'ID de la nouvelle pool
        logger.info(f"Nouvelle poule ajoutée: {pool_name} ({pool_code})")
        return new_pool
    else:
        changes = []

        if existing_pool.pool_name != pool_name:
            changes.append(f"pool_name: {existing_pool.pool_name} -> {pool_name}")
            existing_pool.pool_name = pool_name

        if existing_pool.division_name != division_name:
            changes.append(f"division_name: {existing_pool.division_name} -> {division_name}")
            existing_pool.division_name = division_name

        if existing_pool.gender != gender:
            changes.append(f"gender: {existing_pool.gender} -> {gender}")
            existing_pool.gender = gender
            
        if existing_pool.division_code != division_code:
            changes.append(f"division_code: {existing_pool.division_code} -> {division_code}")
            existing_pool.division_code = division_code

        if existing_pool.raw_division_name != raw_division_name:
            changes.append(f"raw_division_name: {existing_pool.raw_division_name} -> {raw_division_name}")
            existing_pool.raw_division_name = raw_division_name

        if existing_pool.league_name != league_name:
            changes.append(f"league_name: {existing_pool.league_name} -> {league_name}")
            existing_pool.league_name = league_name

        if not existing_pool.active:
            existing_pool.active = True
            changes.append("Poule réactivée.")

        if changes:
            logger.info(f"Poule {pool_code} ({league_code}) mise à jour. Changements: {', '.join(changes)}")

        return existing_pool

@handle_errors
def desactivate_pools(session, league_code, scraped_pool_codes):
    """
    Désactive les pools qui existent en base de données mais n'ont pas été scrapées.

    Parameters:
    - session: La session SQLAlchemy active.
    - scraped_pool_codes (set): Un ensemble des codes des pools qui ont été scrapés.
    """

    # 1. Désactiver les pools qui ne sont pas dans les pools scrapées
    pools_to_desactivate = session.query(Pool).filter(
        Pool.active == True,
        Pool.league_code == league_code,
        Pool.pool_code.notin_(scraped_pool_codes)
    ).all()
    
    pool_ids_to_desactivate = [pool.id for pool in pools_to_desactivate]
    
    # 2. Désactiver les équipes associées aux pools désactivées
    if pool_ids_to_desactivate:
        teams_to_deactivate = session.query(Team).filter(
            Team.active == True,
            Team.pool_id.in_(pool_ids_to_desactivate)
        ).all()

        for team in teams_to_deactivate:
            team.active = False
            logger.info(f"L'équipe {team.team_name} dans la poule {team.pool.pool_code} a été désactivée.")
            session.add(team)

    # 3. Désactiver les matchs associés aux pools désactivées
    if pool_ids_to_desactivate:
        matches_to_deactivate = session.query(Match).filter(
            Match.active == True,
            Match.pool_id.in_(pool_ids_to_desactivate)
        ).all()

        for match in matches_to_deactivate:
            match.active = False
            logger.info(f"Le match {match.match_code} dans la poule {match.pool.pool_code} a été désactivé.")
            session.add(match)
    
    # Désactiver ces pools
    for pool in pools_to_desactivate:
        pool.active = False
        session.add(pool)
        logger.info(f"La poule {pool.league_code} {pool.pool_code} ({pool.pool_name}) a été désactivée.")
    
def get_pools_with_filters(session: Session, pool_code=None, league_code=None, season=None, active=True):
    """
    Récupère les pools en fonction des filtres fournis.
    
    Parameters:
    - session (Session): La session SQLAlchemy active.
    - pool_code (str, optional): Le code de la pool pour filtrer.
    - league_code (str, optional): Le code de la ligue pour filtrer.
    - season (int, optional): La saison pour filtrer.
    - active (bool, optional): Filtrer sur les pools actives ou inactives. Par défaut, True (active).
    
    Returns:
    - List[Pool]: Liste des pools correspondant aux filtres.
    """
    
    query = session.query(Pool)
    
    if pool_code:
        query = query.filter(Pool.pool_code == pool_code)
    
    if league_code:
        query = query.filter(Pool.league_code == league_code)
    
    if season:
        query = query.filter(Pool.season == season)
    
    if active is not None: 
        query = query.filter(Pool.active == active)
    
    pools = query.all()
    
    return pools