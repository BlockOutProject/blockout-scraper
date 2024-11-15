import aiohttp
import pytest
from aioresponses import aioresponses
from api.pools_api import (
    get_pool_by_code_league_season,
    create_pool,
    update_pool,
    get_active_pools_by_league_code,
    deactivate_pool,
)
from tests.utils.fake_pool_factory import FakePoolFactory

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
async def test_get_pool_by_code_league_season(session, mocked_aioresponses):
    factory = FakePoolFactory()
    pool = factory.create()

    url = f"{POOL_API_URL}/{pool.pool_code}/{pool.league_code}/{pool.season}"
    mocked_aioresponses.get(url, payload=pool.to_dict())

    result = await get_pool_by_code_league_season(session, pool.pool_code, pool.league_code, pool.season)

    assert result.pool_code == pool.pool_code
    assert result.league_code == pool.league_code
    assert result.season == pool.season
    assert result.division_code == pool.division_code
    assert result.active == pool.active


@pytest.mark.asyncio
async def test_create_pool(session, mocked_aioresponses):
    factory = FakePoolFactory()
    pool = factory.create()

    url = POOL_API_URL
    mocked_aioresponses.post(url, payload=pool.to_dict())

    result = await create_pool(session, pool)

    assert result.pool_code == pool.pool_code
    assert result.league_code == pool.league_code
    assert result.season == pool.season
    assert result.division_code == pool.division_code
    assert result.active == pool.active


@pytest.mark.asyncio
async def test_update_pool(session, mocked_aioresponses):
    factory = FakePoolFactory()
    pool = factory.create()

    pool.division_name = "Updated Division"
    pool.active = False

    url = f"{POOL_API_URL}/{pool.id}"
    mocked_aioresponses.put(url, payload=pool.to_dict())

    result = await update_pool(session, pool, changes=["division_name", "active"])

    assert result.division_name == "Updated Division"
    assert result.active is False


@pytest.mark.asyncio
async def test_get_active_pools_by_league_code(session, mocked_aioresponses):
    factory = FakePoolFactory()
    pools = [factory.create() for _ in range(3)]

    league_code = pools[0].league_code
    for pool in pools:
        pool.league_code = league_code

    url = f"{POOL_API_URL}/active?league_code={league_code}"
    mocked_aioresponses.get(url, payload=[pool.to_dict() for pool in pools])

    result = await get_active_pools_by_league_code(session, league_code)

    assert len(result) == 3
    for i, pool in enumerate(result):
        assert pool.pool_code == pools[i].pool_code
        assert pool.division_code == pools[i].division_code