import aiohttp
import pytest
from aioresponses import aioresponses
from api.matches_api import (
    get_match_by_league_and_code,
    get_active_matches_by_pool_id,
    create_match,
    update_match,
    get_match_by_pool_teams_date,
)
from models.match import MatchStatus
from tests.utils.fake_match_factory import FakeMatchFactory

MATCH_API_URL = 'http://localhost:8083/api/matches'

@pytest.fixture
async def session():
    async with aiohttp.ClientSession() as session:
        yield session

@pytest.fixture
def mocked_aioresponses():
    with aioresponses(strict=True) as m:
        yield m


@pytest.mark.asyncio
async def test_get_match_by_league_and_code(session, mocked_aioresponses):
    # Préparer un match factice
    factory = FakeMatchFactory()
    match = factory.create()

    # Simuler la réponse de l'API
    url = f"{MATCH_API_URL}/{match.league_code}/{match.match_code}"
    mock_response = match.to_dict()

    # Utiliser le mock pour intercepter l'appel HTTP
    mocked_aioresponses.get(url, payload=mock_response)

    # Appeler la fonction à tester
    result = await get_match_by_league_and_code(session, match.league_code, match.match_code)

    # Assertions
    assert result.id == match.id
    assert result.match_code == match.match_code
    assert result.status == match.status
    assert result.pool_id == match.pool_id


@pytest.mark.asyncio
async def test_get_active_matches_by_pool_id(session, mocked_aioresponses):
    # Préparer des matchs factices
    factory = FakeMatchFactory()
    matches = [factory.create() for _ in range(2)]

    pool_id = matches[0].pool_id  # Même pool_id pour tous les matchs
    for match in matches:
        match.pool_id = pool_id

    # Simuler la réponse de l'API
    url = f"{MATCH_API_URL}/active?pool_id={pool_id}"
    mock_response = [match.to_dict() for match in matches]

    # Utiliser le mock
    mocked_aioresponses.get(url, payload=mock_response)

    # Appeler la fonction à tester
    result = await get_active_matches_by_pool_id(session, pool_id)

    # Assertions
    assert len(result) == len(matches)
    for i, match in enumerate(result):
        assert match.pool_id == matches[i].pool_id
        assert match.match_code == matches[i].match_code


@pytest.mark.asyncio
async def test_create_match(session, mocked_aioresponses):
    # Préparer un match factice
    factory = FakeMatchFactory()
    match = factory.create()

    # Simuler la réponse de l'API
    url = MATCH_API_URL
    mock_response = match.to_dict()

    # Utiliser le mock
    mocked_aioresponses.post(url, payload=mock_response)

    # Appeler la fonction à tester
    result = await create_match(session, match)

    # Assertions
    assert result.id == match.id
    assert result.match_code == match.match_code
    assert result.status == match.status


@pytest.mark.asyncio
async def test_update_match(session, mocked_aioresponses):
    # Préparer un match factice
    factory = FakeMatchFactory()
    match = factory.create()
    match.id = 1

    # Mettre à jour un attribut
    match.status = MatchStatus.FINISHED

    # Simuler la réponse de l'API
    url = f"{MATCH_API_URL}/{match.id}"
    mock_response = match.to_dict()

    # Utiliser le mock
    mocked_aioresponses.put(url, payload=mock_response)

    # Appeler la fonction à tester
    result = await update_match(session, match, changes=["status"])

    # Assertions
    assert result.id == match.id
    assert result.status == MatchStatus.FINISHED


@pytest.mark.asyncio
async def test_get_match_by_pool_teams_date(session, mocked_aioresponses):
    # Préparer un match factice
    factory = FakeMatchFactory()
    match = factory.create()

    # Simuler la réponse de l'API avec les paramètres dans l'URL
    match_date = match.match_date.isoformat()  # ISO 8601 format pour match_date
    url = (
        f"{MATCH_API_URL}/search?"
        f"pool_id={match.pool_id}&team_id_a={match.team_id_a}"
        f"&team_id_b={match.team_id_b}&match_date={match_date}"
    )
    mock_response = match.to_dict()

    # Utiliser le mock
    mocked_aioresponses.get(url, payload=mock_response)

    # Appeler la fonction à tester
    result = await get_match_by_pool_teams_date(
        session,
        match.pool_id,
        match.team_id_a,
        match.team_id_b,
        match.match_date,
    )

    # Assertions
    assert result.id == match.id
    assert result.match_code == match.match_code
    assert result.status == match.status
    