from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class PoolDivisionCode(Enum):
    REG = "REG"
    NAT = "NAT"
    PRO = "PRO"

@dataclass
class Pool:
    pool_code: str
    league_code: str
    season: int
    division_code: PoolDivisionCode
    last_update: Optional[datetime] = None
    id: Optional[int] = None
    league_name: Optional[str] = None
    pool_name: Optional[str] = None
    division_name: Optional[str] = None
    gender: Optional[str] = None
    raw_division_name: Optional[str] = None
    active: bool = True
