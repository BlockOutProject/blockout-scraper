import pytest
from db import Match, MatchStatus
from services.matchs_service import add_match, clear_matchs_table
from services.teams_service import add_team
from services.pools_service import add_pool
from datetime import datetime

@pytest.fixture
def setup_data(db_session):
    """
    Fixture pour préparer les données communes (une poule, deux équipes).
    """
    pool = add_pool(
        session=db_session,
        pool_code='TEST_POOL',
        league_code='TEST_LEAGUE',
        season=2023,
        league_name='Test League',
        pool_name='Test Pool',
        division='Test Division',
        gender='M'
    )
    team_a = add_team(
        session=db_session,
        club_id='CLUB_A',
        pool_id=pool.id,
        team_name='Team A'
    )
    team_b = add_team(
        session=db_session,
        club_id='CLUB_B',
        pool_id=pool.id,
        team_name='Team B'
    )
    return pool, team_a, team_b

def test_add_match(db_session, setup_data):
    """
    Test d'ajout d'un nouveau match avec tous les paramètres spécifiés.
    """
    pool, team_a, team_b = setup_data
    match_date = datetime(2023, 10, 1, 15, 0)

    match = add_match(
        session=db_session,
        league_code='TEST_LEAGUE',
        match_code='MATCH123',
        pool_id=pool.id,
        team_a_id=team_a.id,
        team_b_id=team_b.id,
        match_date=match_date,
        score='3-0',
        status=MatchStatus.COMPLETED.value,  # Utilisation de l'énumération
        venue='Test Venue',
        referee1='Referee 1',
        referee2='Referee 2'
    )

    # Vérifier que le match a bien été ajouté
    assert match.id is not None
    assert match.score == '3-0'
    assert match.status == MatchStatus.COMPLETED
    assert match.venue == 'Test Venue'
    assert match.referee1 == 'Referee 1'
    assert match.referee2 == 'Referee 2'

def test_add_match_without_optional_params(db_session, setup_data):
    """
    Test d'ajout d'un match sans certains paramètres optionnels.
    """
    pool, team_a, team_b = setup_data
    match_date = datetime(2023, 10, 1, 15, 0)

    match = add_match(
        session=db_session,
        league_code='TEST_LEAGUE',
        match_code='MATCH124',
        pool_id=pool.id,
        team_a_id=team_a.id,
        team_b_id=team_b.id,
        match_date=match_date,
        score=None,
        status=MatchStatus.UPCOMING.value  # Aucun score n'est encore disponible
    )

    # Vérifier que le match a bien été ajouté, avec les valeurs optionnelles nulles
    assert match.id is not None
    assert match.score is None
    assert match.venue is None
    assert match.referee1 is None
    assert match.referee2 is None
    assert match.status == MatchStatus.UPCOMING

def test_update_existing_match(db_session, setup_data):
    """
    Test de la mise à jour d'un match existant.
    """
    pool, team_a, team_b = setup_data
    match_date = datetime(2023, 10, 1, 15, 0)

    # Ajouter un match
    match1 = add_match(
        session=db_session,
        league_code='TEST_LEAGUE',
        match_code='MATCH125',
        pool_id=pool.id,
        team_a_id=team_a.id,
        team_b_id=team_b.id,
        match_date=match_date,
        score='3-0',
        status=MatchStatus.COMPLETED.value
    )

    # Mettre à jour ce match avec un score différent
    match2 = add_match(
        session=db_session,
        league_code='TEST_LEAGUE',
        match_code='MATCH125',
        pool_id=pool.id,
        team_a_id=team_a.id,
        team_b_id=team_b.id,
        match_date=match_date,
        score='3-1',
        status=MatchStatus.COMPLETED.value
    )

    # Vérifier que l'ID reste le même (mise à jour), mais que le score a changé
    assert match1.id == match2.id
    assert match2.score == '3-1'

def test_clear_matchs_table(db_session, setup_data):
    """
    Test de la suppression de tous les matchs de la table.
    """
    pool, team_a, team_b = setup_data
    match_date = datetime(2023, 10, 1, 15, 0)

    # Ajouter plusieurs matchs
    add_match(
        session=db_session,
        league_code='TEST_LEAGUE',
        match_code='MATCH126',
        pool_id=pool.id,
        team_a_id=team_a.id,
        team_b_id=team_b.id,
        match_date=match_date,
        score='3-0',
        status=MatchStatus.COMPLETED.value
    )

    add_match(
        session=db_session,
        league_code='TEST_LEAGUE',
        match_code='MATCH127',
        pool_id=pool.id,
        team_a_id=team_a.id,
        team_b_id=team_b.id,
        match_date=match_date,
        score='3-1',
        status=MatchStatus.COMPLETED.value
    )

    clear_matchs_table(session=db_session)

    remaining_matches = db_session.query(Match).all()
    assert len(remaining_matches) == 0

def test_add_match_with_missing_required_fields(db_session, setup_data):
    """
    Test pour ajouter un match avec des champs non nullables manquants.
    Cela devrait lever des exceptions pour chaque champ obligatoire manquant.
    """
    pool, team_a, team_b = setup_data

    # Test 1: match_code manquant
    with pytest.raises(ValueError, match="match_code est obligatoire pour ajouter un match."):
        add_match(
            session=db_session,
            league_code='TEST_LEAGUE',
            match_code=None,  # match_code est obligatoire
            pool_id=pool.id,
            team_a_id=team_a.id,
            team_b_id=team_b.id,
            match_date=datetime(2023, 10, 1, 15, 0),
            score='3-0',
            status=MatchStatus.UPCOMING.value
        )

    # Test 2: league_code manquant
    with pytest.raises(ValueError, match="league_code est obligatoire pour ajouter un match."):
        add_match(
            session=db_session,
            league_code=None,  # league_code est obligatoire
            match_code='MATCH131',
            pool_id=pool.id,
            team_a_id=team_a.id,
            team_b_id=team_b.id,
            match_date=datetime(2023, 10, 1, 15, 0),
            score='3-0',
            status=MatchStatus.UPCOMING.value
        )

    # Test 3: team_a_id manquant
    with pytest.raises(ValueError, match="team_a_id est obligatoire pour ajouter un match."):
        add_match(
            session=db_session,
            league_code='TEST_LEAGUE',
            match_code='MATCH132',
            pool_id=pool.id,
            team_a_id=None,  # team_a_id est obligatoire
            team_b_id=team_b.id,
            match_date=datetime(2023, 10, 1, 15, 0),
            score='3-0',
            status=MatchStatus.UPCOMING.value
        )

    # Test 4: team_b_id manquant
    with pytest.raises(ValueError, match="team_b_id est obligatoire pour ajouter un match."):
        add_match(
            session=db_session,
            league_code='TEST_LEAGUE',
            match_code='MATCH133',
            pool_id=pool.id,
            team_a_id=team_a.id,
            team_b_id=None,  # team_b_id est obligatoire
            match_date=datetime(2023, 10, 1, 15, 0),
            score='3-0',
            status=MatchStatus.UPCOMING.value
        )

    # Test 5: status manquant
    with pytest.raises(ValueError, match="status est obligatoire pour ajouter un match."):
        add_match(
            session=db_session,
            league_code='TEST_LEAGUE',
            match_code='MATCH134',
            pool_id=pool.id,
            team_a_id=team_a.id,
            team_b_id=team_b.id,
            match_date=datetime(2023, 10, 1, 15, 0),
            score='3-0',
            status=None  # status est obligatoire
        )
        
def test_add_match_with_invalid_status(db_session, setup_data):
    """
    Test pour ajouter un match avec un status invalide.
    Cela devrait lever une exception ValueError.
    """
    pool, team_a, team_b = setup_data

    with pytest.raises(ValueError, match="Le statut 'invalid_status' n'est pas valide. Utilisez 'upcoming' ou 'completed'."):
        add_match(
            session=db_session,
            league_code='TEST_LEAGUE',
            match_code='MATCH135',
            pool_id=pool.id,
            team_a_id=team_a.id,
            team_b_id=team_b.id,
            match_date=datetime(2023, 10, 1, 15, 0),
            score='3-0',
            status='invalid_status'
        )
    
def test_clear_empty_matchs_table(db_session):
    """
    Test de la suppression de tous les matchs lorsqu'il n'y a aucun match dans la table.
    """
    clear_matchs_table(session=db_session)

    remaining_matches = db_session.query(Match).all()
    assert len(remaining_matches) == 0 
    
def test_add_duplicate_match(db_session, setup_data):
    """
    Test pour vérifier qu'un match avec le même match_code et league_code ne crée pas de doublon.
    """
    pool, team_a, team_b = setup_data
    match_date = datetime(2023, 10, 1, 15, 0)

    # Ajouter un match
    add_match(
        session=db_session,
        league_code='TEST_LEAGUE',
        match_code='MATCH136',
        pool_id=pool.id,
        team_a_id=team_a.id,
        team_b_id=team_b.id,
        match_date=match_date,
        score='3-0',
        status=MatchStatus.COMPLETED.value
    )

    duplicate_match = add_match(
        session=db_session,
        league_code='TEST_LEAGUE',
        match_code='MATCH136',
        pool_id=pool.id,
        team_a_id=team_a.id,
        team_b_id=team_b.id,
        match_date=match_date,
        score='3-1',
        status=MatchStatus.COMPLETED.value
    )

    all_matches = db_session.query(Match).all()
    assert len(all_matches) == 1 
    assert duplicate_match.score == '3-1'
        
def test_update_multiple_fields(db_session, setup_data):
    """
    Test de la mise à jour de plusieurs champs d'un match existant.
    """
    pool, team_a, team_b = setup_data
    match_date = datetime(2023, 10, 1, 15, 0)

    # Ajouter un match
    match = add_match(
        session=db_session,
        league_code='TEST_LEAGUE',
        match_code='MATCH138',
        pool_id=pool.id,
        team_a_id=team_a.id,
        team_b_id=team_b.id,
        match_date=match_date,
        score='3-0',
        status=MatchStatus.COMPLETED.value
    )

    # Mise à jour de plusieurs champs
    updated_match = add_match(
        session=db_session,
        league_code='TEST_LEAGUE',
        match_code='MATCH138',
        pool_id=pool.id,
        team_a_id=team_b.id,  # Inverser les équipes
        team_b_id=team_a.id,
        match_date=datetime(2023, 10, 2, 16, 0),  # Nouvelle date
        score='3-2',
        status=MatchStatus.UPCOMING.value,  # Nouveau statut
        venue='New Venue'
    )

    # Vérifier que les champs ont été mis à jour correctement
    assert updated_match.team_a_id == team_b.id
    assert updated_match.team_b_id == team_a.id
    assert updated_match.match_date == datetime(2023, 10, 2, 16, 0)
    assert updated_match.score == '3-2'
    assert updated_match.status == MatchStatus.UPCOMING
    assert updated_match.venue == 'New Venue'