import aiohttp
import pytest
from aioresponses import aioresponses
from models.match import MatchStatus
from services.matchs_service import add_or_update_match, deactivate_matches
from tests.utils.fake_match_factory import FakeMatchFactory

MATCH_API_URL = "http://localhost:8083/api/matches"

@pytest.fixture
async def session():
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture
def mocked_aioresponses():
    with aioresponses(strict=True) as m:
        yield m
        
@pytest.mark.asyncio
async def test_add_or_update_match_create_new(session, mocked_aioresponses):
    factory = FakeMatchFactory()
    match = factory.create()

    url_get = f"{MATCH_API_URL}/{match.league_code}/{match.match_code}"
    url_post = MATCH_API_URL

    # Simuler qu'aucun match existant n'est trouvé
    mocked_aioresponses.get(url_get, status=204)

    # Simuler la création d'un nouveau match
    mocked_aioresponses.post(url_post, payload=match.to_dict())

    result = await add_or_update_match(session, match)

    assert result.match_code == match.match_code
    assert result.league_code == match.league_code
    assert result.team_id_a == match.team_id_a
    assert result.team_id_b == match.team_id_b


@pytest.mark.asyncio
async def test_add_or_update_match_update_existing(session, mocked_aioresponses):
    factory = FakeMatchFactory()
    existing_match = factory.create()
    updated_match = factory.create()

    updated_match.id = existing_match.id
    updated_match.match_code = existing_match.match_code
    updated_match.league_code = existing_match.league_code
    updated_match.status = MatchStatus.FINISHED

    url_get = f"{MATCH_API_URL}/{existing_match.league_code}/{existing_match.match_code}"
    url_put = f"{MATCH_API_URL}/{existing_match.id}"

    # Simuler qu'un match existant est trouvé
    mocked_aioresponses.get(url_get, payload=existing_match.to_dict())

    # Simuler la mise à jour du match
    mocked_aioresponses.put(url_put, payload=updated_match.to_dict())

    result = await add_or_update_match(session, updated_match)

    assert result.id == existing_match.id
    assert result.status == MatchStatus.FINISHED