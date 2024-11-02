from typing import Optional, List, Dict, Union
import aiohttp

from typing import Optional, Dict, Union
import aiohttp
import logging
from api.matchs_api import deactivate_match, get_active_matches_by_pool_id
from api.pools_api import create_pool, deactivate_pool, get_active_pools_by_league_code, get_pool_by_code_league_season, update_pool
from api.teams_api import deactivate_team, get_active_teams_by_pool_id
from models.pool import Pool

logger = logging.getLogger('blockout')

async def add_or_update_pool(session: aiohttp.ClientSession, pool: Pool) -> Optional[Pool]:
    """
    Vérifie si une pool existe et la met à jour ou la crée selon les besoins.
    
    Retourne la pool ajoutée ou mise à jour si une modification a été effectuée.
    """
    required_fields = ['pool_code', 'league_code', 'season', 'pool_name', 'division_code', 'division_name']
    
    for field in required_fields:
        if not getattr(pool, field, None):
            raise ValueError(f"{field} est obligatoire pour ajouter ou mettre à jour une pool.")

    existing_pool = await get_pool_by_code_league_season(session, pool.pool_code, pool.league_code, pool.season)
    
    if existing_pool:
        changes = []
        pool.id = existing_pool.id

        if existing_pool.pool_name != pool.pool_name:
            changes.append(f"pool_name: {existing_pool.pool_name} -> {pool.pool_name}")
        
        if existing_pool.division_name != pool.division_name:
            changes.append(f"division_name: {existing_pool.division_name} -> {pool.division_name}")
        
        if existing_pool.gender != pool.gender:
            changes.append(f"gender: {existing_pool.gender} -> {pool.gender}")

        if existing_pool.division_code != pool.division_code:
            changes.append(f"division_code: {existing_pool.division_code} -> {pool.division_code}")

        if not existing_pool.active:
            pool.active = True
            changes.append(f"Pool {existing_pool.id} réactivée.")

        if changes:
            logger.info(f"Pool {existing_pool.pool_code} (ID: {existing_pool.id}) mise à jour avec les changements suivants: {', '.join(changes)}")
            return await update_pool(session, pool, changes)
        else:
            return existing_pool
    else:
        return await create_pool(session, pool)
    
async def deactivate_pools(session: aiohttp.ClientSession, league_code: str, scraped_pool_codes: set) -> None:
    """
    Désactive les pools, équipes et matchs qui n'ont pas été scrapés pour une ligue spécifique.
    
    Ne retourne rien, mais logue les désactivations effectuées.
    """
    pools = await get_active_pools_by_league_code(session, league_code)
    if pools is None:
        return

    pools_to_deactivate = [pool for pool in pools if pool.pool_code not in scraped_pool_codes]
    pool_ids_to_deactivate = [pool.id for pool in pools_to_deactivate]

    # Désactiver les équipes associées aux pools désactivées
    for pool_id in pool_ids_to_deactivate:
        teams = await get_active_teams_by_pool_id(session, pool_id)
        if teams:
            for team in teams:
                await deactivate_team(session, team.id)

    # Désactiver les matchs associés aux pools désactivées
    for pool_id in pool_ids_to_deactivate:
        matches = await get_active_matches_by_pool_id(session, pool_id)
        if matches:
            for match in matches:
                await deactivate_match(session, match.id)

    # Désactiver les pools
    for pool_id in pool_ids_to_deactivate:
        await deactivate_pool(session, pool_id)