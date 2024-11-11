from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import datetime

class MatchStatus(Enum):
    UPCOMING = "UPCOMING"
    FINISHED = "FINISHED"

@dataclass
class Match:
    match_code: str
    league_code: str
    pool_id: int
    team_id_a: int
    team_id_b: int
    match_date: datetime
    status: MatchStatus
    last_update: Optional[datetime] = None
    id: Optional[int] = None
    set: Optional[str] = None
    score: Optional[str] = None
    venue: Optional[str] = None
    referee1: Optional[str] = None
    referee2: Optional[str] = None
    live_code: Optional[int] = None
    active: bool = True
