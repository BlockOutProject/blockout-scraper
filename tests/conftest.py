import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import Base

@pytest.fixture(scope='session')
def engine():
    test_engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    test_engine.dispose()

@pytest.fixture(scope='function')
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()