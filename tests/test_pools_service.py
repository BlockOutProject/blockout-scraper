import pytest
from services.pools_service import add_pool

def test_add_pool(db_session):
    pool = add_pool(
        session=db_session,
        pool_code='TEST_POOL',
        league_code='TEST_LEAGUE',
        season=2023,
        league_name='Test League',
        pool_name='Test Pool',
        division='Test Division',
        gender='M',
        raw_division='Test Division Raw'
    )
    assert pool.id is not None
    assert pool.pool_code == 'TEST_POOL'

def test_add_existing_pool(db_session):
    pool1 = add_pool(
        session=db_session,
        pool_code='TEST_POOL',
        league_code='TEST_LEAGUE',
        season=2023,
        league_name='Test League',
        pool_name='Test Pool',
        division='Test Division',
        gender='M'
    )
    pool2 = add_pool(
        session=db_session,
        pool_code='TEST_POOL',
        league_code='TEST_LEAGUE',
        season=2023,
        league_name='Test League Duplicate',
        pool_name='Duplicate Pool Name',
        division='Test Division',
        gender='M'
    )
    assert pool1.id == pool2.id
    assert pool2.league_name == 'Test League'  # Le nom initial est conservé