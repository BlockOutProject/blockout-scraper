# tests/test_teams_service.py
import pytest
from services.teams_service import add_team, get_team
from services.pools_service import add_pool

@pytest.fixture
def test_pool(db_session):
    return add_pool(
        session=db_session,
        pool_code='TEST_POOL',
        league_code='TEST_LEAGUE',
        season=2023,
        league_name='Test League',
        pool_name='Test Pool',
        division='Test Division',
        gender='M'
    )

def test_add_team(db_session, test_pool):
    team = add_team(
        session=db_session,
        club_id='CLUB123',
        pool_id=test_pool.id,
        team_name='Test Team'
    )
    assert team.id is not None
    assert team.team_name == 'Test Team'

def test_get_team(db_session, test_pool):
    add_team(
        session=db_session,
        club_id='CLUB123',
        pool_id=test_pool.id,
        team_name='Test Team'
    )
    team = get_team(
        session=db_session,
        pool_id=test_pool.id,
        club_id='CLUB123'
    )
    assert team is not None
    assert team.team_name == 'Test Team'