import aiohttp
import pytest
from aioresponses import aioresponses
from services.teams_service import add_or_update_team
from tests.utils.fake_team_factory import FakeTeamFactory
from urllib.parse import urlencode

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
async def test_add_or_update_team_create_new(session, mocked_aioresponses):
    factory = FakeTeamFactory()
    team = factory.create()

    url_get = f"{TEAM_API_URL}/search?pool_id={team.pool_id}&team_name={team.team_name}"
    url_post = TEAM_API_URL

    # Simuler qu'aucune équipe existante n'est trouvée
    mocked_aioresponses.get(url_get, status=204)

    # Simuler la création d'une nouvelle équipe
    mocked_aioresponses.post(url_post, payload=team.to_dict())

    result = await add_or_update_team(session, team)

    assert result.team_name == team.team_name
    assert result.pool_id == team.pool_id
    assert result.club_id == team.club_id


@pytest.mark.asyncio
async def test_add_or_update_team_update_existing(session, mocked_aioresponses):
    factory = FakeTeamFactory()
    existing_team = factory.create()
    updated_team = factory.create()

    updated_team.id = existing_team.id
    updated_team.pool_id = existing_team.pool_id
    updated_team.team_name = existing_team.team_name
    updated_team.club_id = "New Club ID"

    url_get = f"{TEAM_API_URL}/search?pool_id={existing_team.pool_id}&team_name={existing_team.team_name}"
    url_put = f"{TEAM_API_URL}/{existing_team.id}"

    # Simuler qu'une équipe existante est trouvée
    mocked_aioresponses.get(url_get, payload=existing_team.to_dict())

    # Simuler la mise à jour de l'équipe
    mocked_aioresponses.put(url_put, payload=updated_team.to_dict())

    result = await add_or_update_team(session, updated_team)

    assert result.id == existing_team.id
    assert result.club_id == "New Club ID"