from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Boolean, UniqueConstraint, Enum
from sqlalchemy.orm import relationship
from .base import Base
from enum import Enum as PyEnum

class PoolDivisionCode(PyEnum):
    REG = "REG"
    NAT = "NAT"
    PRO = "PRO"

class Pool(Base):
    __tablename__ = 'pools'

    id = Column(Integer, primary_key=True)
    pool_code = Column(String, nullable=False)
    league_code = Column(String, nullable=False)
    season = Column(Integer, nullable=False)
    league_name = Column(String)
    pool_name = Column(String)
    division_code = Column(Enum(PoolDivisionCode), nullable=False)
    division_name = Column(String)
    gender = Column(String)
    raw_division_name = Column(String)
    last_update = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    active = Column(Boolean, default=True)

    teams = relationship('Team', back_populates='pool', cascade='all, delete-orphan')
    matches = relationship('Match', back_populates='pool', cascade='all, delete-orphan')

    __table_args__ = (
        UniqueConstraint('pool_code', 'league_code', 'season', name='uix_pool'),
    )