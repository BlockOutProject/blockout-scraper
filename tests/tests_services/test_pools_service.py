import aiohttp
import pytest
from aioresponses import aioresponses
from services.pools_service import add_or_update_pool, deactivate_pools
from tests.utils.fake_pool_factory import FakePoolFactory
from urllib.parse import urlencode

POOL_API_URL = "http://localhost:8081/api/pools"

@pytest.fixture
async def session():
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture
def mocked_aioresponses():
    with aioresponses(strict=True) as m:
        yield m
        
@pytest.mark.asyncio
async def test_add_or_update_pool_create_new(session, mocked_aioresponses):
    factory = FakePoolFactory()
    pool = factory.create()

    url_get = f"{POOL_API_URL}/{pool.pool_code}/{pool.league_code}/{pool.season}"
    url_post = POOL_API_URL

    # Simuler qu'aucune pool existante n'est trouvée
    mocked_aioresponses.get(url_get, status=204)

    # Simuler la création d'une nouvelle pool
    mocked_aioresponses.post(url_post, payload=pool.to_dict())

    result = await add_or_update_pool(session, pool)

    assert result.pool_code == pool.pool_code
    assert result.league_code == pool.league_code
    assert result.season == pool.season
    assert result.pool_name == pool.pool_name


@pytest.mark.asyncio
async def test_add_or_update_pool_update_existing(session, mocked_aioresponses):
    factory = FakePoolFactory()
    existing_pool = factory.create()
    updated_pool = factory.create()

    updated_pool.id = existing_pool.id
    updated_pool.pool_code = existing_pool.pool_code
    updated_pool.league_code = existing_pool.league_code
    updated_pool.season = existing_pool.season
    updated_pool.pool_name = "Updated Pool Name"

    url_get = f"{POOL_API_URL}/{existing_pool.pool_code}/{existing_pool.league_code}/{existing_pool.season}"
    url_put = f"{POOL_API_URL}/{existing_pool.id}"

    # Simuler qu'une pool existante est trouvée
    mocked_aioresponses.get(url_get, payload=existing_pool.to_dict())

    # Simuler la mise à jour de la pool
    mocked_aioresponses.put(url_put, payload=updated_pool.to_dict())

    result = await add_or_update_pool(session, updated_pool)

    assert result.id == existing_pool.id
    assert result.pool_name == "Updated Pool Name"