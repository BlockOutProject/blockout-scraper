from typing import Optional
import aiohttp
from api.pools_api import create_pool, deactivate_pool, get_active_pools_by_league_code, update_pool
from models.pool import Pool
from utils.handlers.error_handler import handle_errors
from config.logger_config import logger

@handle_errors
async def add_or_update_pool(session: aiohttp.ClientSession, pool: Pool, existing_pool: Optional[Pool]) -> Pool:
    """
    Vérifie si une pool existe et la met à jour ou la crée selon les besoins.
    """
    required_fields = ['pool_code', 'league_code', 'season', 'pool_name', 'division_code', 'division_name']
    missing_fields = [field for field in required_fields if not getattr(pool, field, None)]
    if missing_fields:
        raise ValueError(f"Les champs obligatoires suivants sont manquants : {', '.join(missing_fields)}.")

    if existing_pool:
        changes = []
        pool.id = existing_pool.id

        for field in ['pool_name', 'division_name', 'gender', 'division_code']:
            if getattr(existing_pool, field, None) != getattr(pool, field, None):
                changes.append(f"{field}: {getattr(existing_pool, field)} -> {getattr(pool, field)}")

        if not existing_pool.active:
            pool.active = True
            changes.append("Pool réactivée.")

        if changes:
            return await update_pool(session, pool, changes)
        return existing_pool
    else:
        new_pool = await create_pool(session, pool)
        logger.info(f"Pool {pool.pool_code} créée avec succès.")
        return new_pool


@handle_errors
async def deactivate_pools(session: aiohttp.ClientSession, league_code: str, scraped_pool_codes: set) -> None:
    """
    Désactive les pools qui n'ont pas été scrapées pour une ligue spécifique.
    """
    pools = await get_active_pools_by_league_code(session, league_code)
    if not pools:
        return

    pools_to_deactivate = [pool for pool in pools if pool.pool_code not in scraped_pool_codes]
    for pool in pools_to_deactivate:
        try:
            await deactivate_pool(session, pool.id)
            logger.info(f"Pool {pool.pool_code} (ID: {pool.id}) désactivée avec succès.")
        except Exception as e:
            logger.error(f"Erreur lors de la désactivation de la pool {pool.pool_code} (ID: {pool.id}): {e}")