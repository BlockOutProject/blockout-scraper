from urllib.parse import urlencode
import aiohttp
import pytest
from aioresponses import aioresponses
from api.teams_api import (
    get_team_by_pool_and_name,
    create_team,
    update_team,
    get_active_teams_by_pool_id,
)
from tests.utils.fake_team_factory import FakeTeamFactory

TEAM_API_URL = "http://localhost:8082/api/teams"


@pytest.fixture
async def session():
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture
def mocked_aioresponses():
    with aioresponses(strict=True) as m:
        yield m


@pytest.mark.asyncio
async def test_get_team_by_pool_and_name(session, mocked_aioresponses):
    factory = FakeTeamFactory()
    team = factory.create()

    params = urlencode({'pool_id': team.pool_id, 'team_name': team.team_name})
    url = f"{TEAM_API_URL}/search?{params}"

    mocked_aioresponses.get(url, payload=team.to_dict())

    result = await get_team_by_pool_and_name(session, team.pool_id, team.team_name)

    assert result.team_name == team.team_name
    assert result.pool_id == team.pool_id
    assert result.active == team.active


@pytest.mark.asyncio
async def test_create_team(session, mocked_aioresponses):
    factory = FakeTeamFactory()
    team = factory.create()

    url = TEAM_API_URL
    mocked_aioresponses.post(url, payload=team.to_dict())

    result = await create_team(session, team)

    assert result.team_name == team.team_name
    assert result.club_id == team.club_id
    assert result.pool_id == team.pool_id
    assert result.active == team.active


@pytest.mark.asyncio
async def test_update_team(session, mocked_aioresponses):
    factory = FakeTeamFactory()
    team = factory.create()

    team.team_name = "Updated Team Name"
    team.active = False

    url = f"{TEAM_API_URL}/{team.id}"
    mocked_aioresponses.put(url, payload=team.to_dict())

    result = await update_team(session, team, changes=["team_name", "active"])

    assert result.team_name == "Updated Team Name"
    assert result.active is False


@pytest.mark.asyncio
async def test_get_active_teams_by_pool_id(session, mocked_aioresponses):
    factory = FakeTeamFactory()
    teams = [factory.create() for _ in range(3)]

    pool_id = teams[0].pool_id
    for team in teams:
        team.pool_id = pool_id

    url = f"{TEAM_API_URL}/active?pool_id={pool_id}"
    mocked_aioresponses.get(url, payload=[team.to_dict() for team in teams])

    result = await get_active_teams_by_pool_id(session, pool_id)

    assert len(result) == 3
    for i, team in enumerate(result):
        assert team.team_name == teams[i].team_name
        assert team.pool_id == teams[i].pool_id