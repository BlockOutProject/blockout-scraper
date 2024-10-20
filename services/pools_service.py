from typing import Optional
import aiohttp
from sqlalchemy.orm import Session
from api.pools_api import create_pool, get_pool_by_code_league_season, update_pool
from errors_handler import handle_errors
import logging
from models.match import Match
from models.pool import Pool
from models.team import Team

logger = logging.getLogger('blockout')

POOL_API_URL = 'http://localhost:8081/api/pools'

async def add_or_update_pool(session: aiohttp.ClientSession, pool_data: dict):
    """
    Vérifie l'existence d'une pool et la met à jour ou la crée selon les besoins.
    """
    required_fields = ['pool_code', 'league_code', 'season', 'pool_name', 'division_code', 'division_name']
    
    for field in required_fields:
        if field not in pool_data or not pool_data[field]:
            raise ValueError(f"{field} est obligatoire pour ajouter ou mettre à jour une pool.")

    existing_pool = await get_pool_by_code_league_season(session, pool_data['pool_code'], pool_data['league_code'], pool_data['season'])
    
    if existing_pool:
        changes = []

        if existing_pool['pool_name'] != pool_data['pool_name']:
            changes.append(f"pool_name: {existing_pool['pool_name']} -> {pool_data['pool_name']}")
        
        if existing_pool['division_name'] != pool_data['division_name']:
            changes.append(f"division_name: {existing_pool['division_name']} -> {pool_data['division_name']}")
        
        if existing_pool['gender'] != pool_data.get('gender'):
            changes.append(f"gender: {existing_pool['gender']} -> {pool_data.get('gender')}")

        if existing_pool['division_code'] != pool_data['division_code']:
            changes.append(f"division_code: {existing_pool['division_code']} -> {pool_data['division_code']}")

        if not existing_pool['active']:
            pool_data['active'] = True
            changes.append("Pool réactivée.")

        if changes:
            return await update_pool(session, existing_pool['id'], pool_data)
        else:
            return existing_pool
    else:
        return await create_pool(session, pool_data)

@handle_errors
def deactivate_pools(session, league_code, scraped_pool_codes):
    """
    Désactive les pools qui existent en base de données mais n'ont pas été scrapées.

    Parameters:
    - session: La session SQLAlchemy active.
    - scraped_pool_codes (set): Un ensemble des codes des pools qui ont été scrapés.
    """

    # 1. Désactiver les pools qui ne sont pas dans les pools scrapées
    pools_to_deactivate = session.query(Pool).filter(
        Pool.active == True,
        Pool.league_code == league_code,
        Pool.pool_code.notin_(scraped_pool_codes)
    ).all()
    
    pool_ids_to_deactivate = [pool.id for pool in pools_to_deactivate]
    
    # 2. Désactiver les équipes associées aux pools désactivées
    if pool_ids_to_deactivate:
        teams_to_deactivate = session.query(Team).filter(
            Team.active == True,
            Team.pool_id.in_(pool_ids_to_deactivate)
        ).all()

        for team in teams_to_deactivate:
            team.active = False
            logger.info(f"L'équipe {team.team_name} dans la poule {team.pool.pool_code} a été désactivée.")
            session.add(team)

    # 3. Désactiver les matchs associés aux pools désactivées
    if pool_ids_to_deactivate:
        matches_to_deactivate = session.query(Match).filter(
            Match.active == True,
            Match.pool_id.in_(pool_ids_to_deactivate)
        ).all()

        for match in matches_to_deactivate:
            match.active = False
            logger.info(f"Le match {match.match_code} dans la poule {match.pool.pool_code} a été désactivé.")
            session.add(match)
    
    # Désactiver ces pools
    for pool in pools_to_deactivate:
        pool.active = False
        session.add(pool)
        logger.info(f"La poule {pool.league_code} {pool.pool_code} ({pool.pool_name}) a été désactivée.")
    