from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    club_id = Column(String, nullable=False)
    pool_id = Column(Integer, ForeignKey('pools.id'), nullable=False)
    team_name = Column(String, nullable=False)

    pool = relationship('Pool', back_populates='teams')
    matches_home = relationship('Match', back_populates='team_a', foreign_keys='Match.team_a_id', cascade='all, delete-orphan')
    matches_away = relationship('Match', back_populates='team_b', foreign_keys='Match.team_b_id', cascade='all, delete-orphan')
    last_update = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    active = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint('pool_id', 'team_name', name='uix_team'),
    )