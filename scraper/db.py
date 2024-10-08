from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import declarative_base

# Déclaration de l'engine pour la connexion à la base de données
DATABASE_URL = "postgresql://admin:password@localhost:5432/myvolley"
engine = create_engine(DATABASE_URL)

# Déclaration de la base
Base = declarative_base()

# Modèles (tables)
class Pool(Base):
    __tablename__ = 'pools'
    id = Column(Integer, primary_key=True)
    pool_code = Column(String(10), nullable=False)
    league_code = Column(String(10), nullable=False)
    season = Column(Integer, nullable=False)
    league_name = Column(String(100), nullable=False)
    pool_name = Column(String(100), nullable=False)
    division = Column(String(50), nullable=False)
    raw_division = Column(String(50), nullable=True)
    gender = Column(Enum('M', 'F', name='gender_enum'), nullable=True)
    __table_args__ = (UniqueConstraint('pool_code', 'league_code', 'season', name='uq_pool_league_season'),)

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    club_id = Column(String(50), nullable=True)
    pool_id = Column(Integer, ForeignKey('pools.id'), nullable=False)
    team_name = Column(String(100), nullable=False)
    __table_args__ = (UniqueConstraint('club_id', 'pool_id', name='uq_club_pool'),)


class Match(Base):
    __tablename__ = 'matches'
    id = Column(Integer, primary_key=True)
    league_code = Column(String(10), nullable=False)
    match_code = Column(String(20), nullable=False)
    pool_id = Column(Integer, ForeignKey('pools.id'), nullable=False)
    team_a_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    team_b_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    match_date = Column(DateTime, nullable=False)
    score = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False)
    venue = Column(String(100), nullable=True)
    referee1 = Column(String(50), nullable=True)
    referee2 = Column(String(50), nullable=True)
    __table_args__ = (UniqueConstraint('league_code', 'match_code', name='uq_league_match_code'),)

# Crée les tables dans la base de données si elles n'existent pas encore
Base.metadata.create_all(bind=engine)