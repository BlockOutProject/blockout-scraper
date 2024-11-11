from typing import Optional
import aiohttp
import logging
from api.pools_api import create_pool, deactivate_pool, get_active_pools_by_league_code, get_pool_by_code_league_season, update_pool
from models.pool import Pool
from utils.handlers.function_name_handler import log_function_name

logger = logging.getLogger('blockout')

@log_function_name
async def add_or_update_pool(session: aiohttp.ClientSession, pool: Pool) -> Optional[Pool]:
    """
    Vérifie si une pool existe et la met à jour ou la crée selon les besoins.
    """
    try:
        # Validation des champs obligatoires
        required_fields = ['pool_code', 'league_code', 'season', 'pool_name', 'division_code', 'division_name']
        missing_fields = [field for field in required_fields if not getattr(pool, field, None)]
        if missing_fields:
            raise ValueError(f"Les champs obligatoires suivants sont manquants : {', '.join(missing_fields)}.")

        # Vérification de l'existence de la pool
        existing_pool = await get_pool_by_code_league_season(session, pool.pool_code, pool.league_code, pool.season)

        if existing_pool:
            # Cas où la pool existe déjà
            changes = []
            pool.id = existing_pool.id

            # Détection des modifications
            for field in ['pool_name', 'division_name', 'gender', 'division_code']:
                if getattr(existing_pool, field, None) != getattr(pool, field, None):
                    changes.append(f"{field}: {getattr(existing_pool, field)} -> {getattr(pool, field)}")

            # Réactivation si nécessaire
            if not existing_pool.active:
                pool.active = True
                changes.append("Pool réactivée.")

            if changes:
                logger.info(f"Pool {existing_pool.pool_code} mise à jour avec les changements : {', '.join(changes)}")
                return await update_pool(session, pool, changes)
            else:
                return existing_pool
        else:
            # Cas où la pool n'existe pas
            new_pool = await create_pool(session, pool)
            logger.info(f"Pool {pool.pool_code} créée avec succès.")
            return new_pool

    except ValueError as e:
        logger.error(f"Erreur de validation pour la pool {pool.pool_code}: {e}")
        raise

    except Exception as e:
        logger.exception(f"Erreur inattendue lors du traitement de la pool {pool.pool_code}: {e}")
        raise
    
@log_function_name
async def deactivate_pools(session: aiohttp.ClientSession, league_code: str, scraped_pool_codes: set) -> None:
    """
    Désactive les pools, équipes et matchs qui n'ont pas été scrapés pour une ligue spécifique.

    Ne retourne rien, mais logue les désactivations effectuées.
    """
    try:
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
                continue

    except Exception as e:
        logger.exception(f"Erreur inattendue lors de la désactivation des pools pour la ligue {league_code}: {e}")
        raise