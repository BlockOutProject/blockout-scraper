from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import Base

class MatchStatus(PyEnum):
    UPCOMING = "upcoming"
    COMPLETED = "completed"

class Match(Base):
    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True)
    match_code = Column(String, nullable=False)
    league_code = Column(String, nullable=False)
    pool_id = Column(Integer, ForeignKey('pools.id'), nullable=False)
    team_a_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    team_b_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    match_date = Column(DateTime, nullable=False)
    set = Column(String)
    score = Column(String)
    status = Column(Enum(MatchStatus), nullable=False)
    venue = Column(String)
    referee1 = Column(String)
    referee2 = Column(String)
    last_update = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    active = Column(Boolean, default=True)

    pool = relationship('Pool', back_populates='matches')
    team_a = relationship('Team', foreign_keys=[team_a_id], back_populates='matches_home')
    team_b = relationship('Team', foreign_keys=[team_b_id], back_populates='matches_away')

    __table_args__ = (
        UniqueConstraint('match_code', 'league_code', name='uix_match'),
    )